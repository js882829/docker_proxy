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

def main():
    if len(sys.argv) != 4:
        print("用法: python uploader.py <username> <password> <registry_url>")
        sys.exit(1)
      
    username = sys.argv[1]
    password = sys.argv[2]
    registry_url = sys.argv[3]

    synced_images = []
    
    # 读取 JSON 文件中的镜像
    try:
        with open('images.json') as file:
            images = json.load(file)
    except FileNotFoundError:
        print("文件 'images.json' 未找到。")
        sys.exit(1)
    except json.JSONDecodeError:
        print("解析 'images.json' 时出错。")
        sys.exit(1)
    
    for image in images:
        try:
            print(f"处理镜像: {image['target']}")
            upload_docker_images(image["source"], image["target"], registry_url, username, password)
            synced_images.append(image)
        except Exception as e:
            print(f"上传镜像 {image['target']} 失败: {e}")

    # 将成功上传的镜像写入 synced_images.json
    with open('synced_images.json', 'w') as file:
        json.dump(synced_images, file, indent=2)

if __name__ == "__main__":
    main()
