from pydantic import BaseModel

from process.assets.setup.images.init_image import init_image_path
from process.assets.setup.images.login_image import login_image_path
from process.assets.setup.images.signup_image import signup_image_path
from process.assets.setup.images.gui_signup_image import gui_signup_image_path
from process.assets.setup.images.face_capture_image import face_capture_image_path


class ImagePaths(BaseModel):
    # main images
    init_img: str = init_image_path
    login_img: str = login_image_path
    signup_img: str = signup_image_path

    # secondary windows
    gui_signup_img: str = gui_signup_image_path
    face_capture_img: str = face_capture_image_path

