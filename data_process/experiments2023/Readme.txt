Each file is named as 

client_<number of clients>_cpu_<number of cpu cores>_mem_<memory limit>_gpu_<number of gpu in use>.csv


Duration of each step detection is recorded.

Typical object detection trace of one image is:

[client]detecting image: image_path  -> [client]image image_name send to server for detection -> [server] detect -> image image_name post detection process 