let video;

let poseNet;
let poses = [];

// set some options for posenet model
let options = {
  architecture: 'MobileNetV1',
  imageScaleFactor: 1,
  outputStride: 16, // (8, 16, 32) The smaller the value, the larger the output resolution, and more accurate the model at the cost of speed
  flipHorizontal: false,
  minConfidence: 0.5,
  maxPoseDetections: 1,
  scoreThreshold: 0.5,
  nmsRadius: 20,
  detectionType: 'single',
  inputResolution: 289, // (161, 193, 257, 289, 321, 353, 385, 417, 449, 481, 513, 801) The larger the value, the more accurate the model at the cost of speed
  multiplier: 1,  // (0.5, 0.75, 1, 1.01) The larger the value, the larger the size of the layers, and more accurate the model at the cost of speed
  quantBytes: 2 // (4, 2, 1)
};

function setup() {
  var canvas = createCanvas(800, 800);
  canvas.parent('sketch-holder');
  
  

  video = createVideo('/static/bicep_curls.mp4');
  // assign poseNet
  poseNet = ml5.poseNet(video, options, modelReady);
  video.volume(0);
  video.speed(0.2);
  video.play();
 
  // set the video size to the size of the canvas (canvas's size will effect the keypoints coordinate)
  //video.size(width, height);
  
  // Hide the video element, and just show the canvas
  video.hide();

  

  // This sets up an event that fills the global variable "poses"
  // with an array every time new poses are detected
  poseNet.on('pose', function (results) {
    poses = results;
    console.log(poses)
  });
 
}

setInterval(sendData, 125);
function sendData() {
  if (poses.length>0){
      if (poses[0].pose.score > 0.05){
        let json_data = {'data-uri': poses[0].pose.keypoints}
      fetch('/predict/', {
        method: 'POST',
        processData: false,
        headers: {
          'Accept': 'application/json, text/plain, */*',
          'Content-Type': 'application/json; charset=utf-8'
        },
        body: JSON.stringify(json_data)
      }).then(res=>res.json())
      .then(res => {
        console.log(res);
        if (res.state != "waiting"){
          document.getElementById("state").innerHTML = res.state;
          document.getElementById("mistake_count").innerHTML = res.mistake_count;
          document.getElementById("success_count").innerHTML = res.success_count;
          document.getElementById("flag").innerHTML = res.flag;
        }
      })
    }
  }
}

function modelReady() {
  select('#status').html('Model Loaded');
}

// A function to draw image on canvas
function draw() {
  background(200)
  image(video, 0, 0);

  // We can call both functions to draw all keypoints and the skeletons
  drawKeypoints();
  drawSkeleton();
}

// A function to draw ellipses over the detected keypoints
function drawKeypoints()  {
  // Loop through all the poses detected
  if (poses.length > 0){
    for (let i = 0; i < poses.length; i++) {
      // For each pose detected, loop through all the keypoints
      let pose = poses[i].pose;
      for (let j = 5; j < pose.keypoints.length; j++) {
        if (![6,8,10].includes(j)){
          // A keypoint is an object describing a body part (like rightArm or leftShoulder)
        let keypoint = pose.keypoints[j];
        // Only draw an ellipse is the pose probability is bigger than 0.6
          if (keypoint.score > 0.6) {
            noStroke();
            fill(255, 0, 0);
            ellipse(keypoint.position.x, keypoint.position.y, 10, 10);
          }
        }
      }
    }
  }
}

// A function to draw the skeletons
function drawSkeleton() {
  // Loop through all the skeletons detected
  if (poses.length > 0){
    for (let i = 0; i < poses.length; i++) {
      let skeleton = poses[i].skeleton;
      // For every skeleton, loop through all body connections
      for (let j = 0; j < skeleton.length; j++) {
        if (![5,6,7].includes(j)){
          let partA = skeleton[j][0];
        let partB = skeleton[j][1];
        stroke(255, 0, 0);
        line(partA.position.x, partA.position.y, partB.position.x, partB.position.y);
        }
      }
    }
  }
}

// function touchStarted() {
//   getAudioContext().resume()
// }

