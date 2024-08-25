import subprocess
import json
import sys

def run_command(command):
    """ 执行命令并处理异常。 """
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"执行命令时出错: {command}")
        print(f"错误信息: {e}")
        raise

def upload_docker_images(source_image, target_image, registry_url, username, password):
    """ 将 Docker 镜像上传到指定的注册表。 """
    # 登录 Docker 注册表
    login_command = f"docker login {registry_url} -u {username} -p {password}"
    run_command(login_command)
    
    # 拉取、标记并推送镜像
    pull_command = f"docker pull {source_image}"
    tag_command = f"docker tag {source_image} {target_image}"
    push_command = f"docker push {target_image}"
    
    run_command(pull_command)
    run_command(tag_command)
    run_command(push_command)
    
    # 登出 Docker 注册表
    logout_command = f"docker logout {registry_url}"
    run_command(logout_command)

def read_json_file(file_path):
    """ 读取 JSON 文件并返回内容。 """
    try:
        with open(file_path) as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"解析 '{file_path}' 时出错。")
        sys.exit(1)

def write_json_file(file_path, data):
    """ 将数据写入 JSON 文件。 """
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=2)
    except IOError as e:
        print(f"写入 '{file_path}' 时出错: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 4:
        print("用法: python uploader.py <username> <password> <registry_url>")
        sys.exit(1)
      
    username = sys.argv[1]
    password = sys.argv[2]
    registry_url = sys.argv[3]

    # 读取已同步的镜像
    synced_images = read_json_file('synced_images.json')

    # 读取待同步的镜像
    images = read_json_file('images.json')

    # 创建一个集合来避免重复
    synced_images_set = {json.dumps(img, sort_keys=True) for img in synced_images}

    for image in images:
        image_str = json.dumps(image, sort_keys=True)
        if image_str not in synced_images_set:
            try:
                print(f"处理镜像: {image['target']}")
                upload_docker_images(image["source"], image["target"], registry_url, username, password)
                synced_images.append(image)
                synced_images_set.add(image_str)
            except Exception as e:
                print(f"上传镜像 {image['target']} 失败: {e}")

    # 将成功上传的镜像写入 synced_images.json
    write_json_file('synced_images.json', synced_images)

if __name__ == "__main__":
    main()
