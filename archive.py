import os
import shutil
import subprocess

from libs.env_enum import EnvEnum
from libs.make_qr_code import make_qr


def upload_itunes_connect(ipa_path):
    """ 上传 iTunes Connect """
    if EnvEnum.ITC_USER.value is None \
            or EnvEnum.ITC_PASSWORD.value is None:
        raise Exception('开发者账号用户名和密码不能为空')
    altool = '$(dirname $(xcode-select -p))/Applications/' \
             'Application\ Loader.app/Contents/Frameworks/' \
             'ITunesSoftwareService.framework/Versions/A/Support/altool'
    subprocess.run('echo "Validating app ..."', shell=True)
    subprocess.run(f'time {altool} --validate-app '
                   f'-f {ipa_path} '
                   f'-u {EnvEnum.ITC_USER.value} '
                   f'-p {EnvEnum.ITC_PASSWORD.value}', shell=True)
    subprocess.run('echo "Uploading app to iTunes Connect ..."', shell=True)
    subprocess.run(f'time {altool} --upload-app '
                   f'-f {ipa_path} '
                   f'-u {EnvEnum.ITC_USER.value} '
                   f'-p {EnvEnum.ITC_PASSWORD.value}', shell=True)


def archive_file(scheme, app_name, icon_path, icon_url):
    """ 处理需要归档的文件 """
    if os.path.exists(EnvEnum.ARCHIVE_PATH.value):
        shutil.rmtree(EnvEnum.ARCHIVE_PATH.value)
    os.mkdir(EnvEnum.ARCHIVE_PATH.value)

    # copy 文件
    archive_ipa_path = f'{EnvEnum.ARCHIVE_PATH.value}/{scheme}.ipa'
    shutil.copy(f'{EnvEnum.BUILD_PATH.value}/{scheme}/{scheme}.ipa',
                archive_ipa_path)
    shutil.copy(f'{EnvEnum.SCRIPT_ITMS_SERVICE_PATH.value}',
                f'{EnvEnum.ARCHIVE_ITMS_SERVICE_PATH.value}')

    # dSYM 文件处理
    dsym_zip = f'{EnvEnum.BUILD_PATH.value}/{scheme}.dsym.zip'
    if os.path.exists(dsym_zip):
        shutil.copy(
            dsym_zip, f'{EnvEnum.ARCHIVE_PATH.value}/{scheme}.dsym.zip')

    credit_plist_url = f'{EnvEnum.ARCHIVE_ITMS_SERVICE_URL.value}'.replace(
        '/', r'\/')
    icon_url = icon_url.replace('/', r'\/')
    # 修改 html 内容
    shutil.copy(
        f'{EnvEnum.SCRIPT_PATH.value}/static/html/trunk_install_release.html',
        f'{EnvEnum.ARCHIVE_PATH.value}/trunk_install_release.html')
    subprocess.run(
        f'sed -i "" "s/BUILD_NUM/{EnvEnum.BUILD_NUM.value}/g" {EnvEnum.ARCHIVE_PATH.value}/trunk_install_release.html',
        shell=True)
    subprocess.run(
        f'sed -i "" "s/PLIST_URL/{credit_plist_url}/g" {EnvEnum.ARCHIVE_PATH.value}/trunk_install_release.html',
        shell=True)
    subprocess.run(
        f'sed -i "" "s/ICON_URL/{icon_url}/g" {EnvEnum.ARCHIVE_PATH.value}/trunk_install_release.html',
        shell=True)
    subprocess.run(
        f'sed -i "" "s/APP_NAME/{app_name}/g" {EnvEnum.ARCHIVE_PATH.value}/trunk_install_release.html',
        shell=True)

    # 生成二维码
    html_url = f'{EnvEnum.ARCHIVE_URL.value}trunk_install_release.html'
    make_qr(
        html_url,
        f'{EnvEnum.SCRIPT_PATH.value}/{icon_path}',
        f'{EnvEnum.ARCHIVE_PATH.value}/{scheme}_iOS_{EnvEnum.BUILD_NUM.value}.png')

    # 上传 iTunes Connect
    if EnvEnum.CONFIGURATION.value == EnvEnum.DIST_CONFIGURATION_NAME.value \
            and EnvEnum.UPLOAD_ITUNES_CONNECT.value == 'true':
        upload_itunes_connect(ipa_path=archive_ipa_path)
