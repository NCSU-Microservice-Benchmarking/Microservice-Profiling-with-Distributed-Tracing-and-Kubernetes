# microservices_client

## environment requirement  
* [Anaconda](https://www.anaconda.com/) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)

## setup environment
1. `conda env create -f environment.yml`  
2. `conda activate microclient`

## use  
run `python run.py`  

## check result
1. go to [Jaeger UI](http://eb2-2259-lin04.csc.ncsu.edu:16687/)
2. in the search box, select service as "pyClient", choose search time range according to your sent request, then click search
3. find the trace result at the right side

## todo list
- [ ] video client  
    - [x] implement basic object detection and tracing  
    - [ ] draw the bounding box according to received detection result, and output the frames with bounding box as images  
    - [ ] output the video with detected bouding box  
- [ ] camera client (potential reference: https://thedatafrog.com/en/articles/human-detection-video/)  
    - [ ] get access to device's camera, if there is any  
    - [ ] implement basic object detection and tracing  
    - [ ] show the detection result in real time  