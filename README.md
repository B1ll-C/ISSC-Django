# ISSC-Django

## Dependencies
Download FFMPEG [Here](https://github.com/BtbN/FFmpeg-Builds/releases)
**ffmpeg-master-latest-win64-gpl**


## Reinstall Packages

### Install via pip
Run the following commands to install the necessary packages:

```bash
pip install deepface==0.0.93 \
            easyocr==1.7.2 \
            h5py==3.12.1 \
            imageio==2.37.0 \
            Keras-Preprocessing==1.1.2 \
            matplotlib==3.10.0 \
            opencv-contrib-python==4.5.5.64 \
            opencv-python==4.5.5.64 \
            opencv-python-headless==4.10.0.84 \
            pandas==2.2.3 \
            retina-face==0.0.17 \
            roboflow==1.1.54 \
            scikit-image==0.25.1 \
            argon2-cffi
```

run this next

```bash
pip install numpy==1.23.5 \
			django \
			mysqlclient \
			tensorflow==2.10.0 \
			whitenoise
```


## env

### API KEY
SECRET_KEY 			= ""
### Database Credentials
DB_NAME 			= ""
DB_USER 			= ""
DB_PASSWORD 		= ""
DB_HOST 			= ""
DB_PORT 			= ""

### Model
ROBOFLOW_API_KEY 	= ""
PROJECT_NAME 		= "issc-plate-recognition"

### SMTP
EMAIL_HOST_USER		= ""
EMAIL_HOST_PASSWORD	= ""