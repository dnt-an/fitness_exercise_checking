let video;

let poseNet;
let poses = [];
var poses_seq = [];



function setup() {
  createCanvas(1200, 1200);
  video = createVideo('../bicep_curls.mp4', vidLoaded);
  video.play();
  video.volume(0);
  // set the video size to the size of the canvas (canvas's size will effect the keypoints coordinate)
  //video.size(width, height);
  
  // Hide the video element, and just show the canvas
  video.hide();
  console.log(video.duration);
}

function vidLoaded(){
  
  // set some options
  let options = {
      architecture: 'MobileNetV1',
      imageScaleFactor: 1,
      outputStride: 8,
      flipHorizontal: false,
      minConfidence: 0.5,
      maxPoseDetections: 5,
      scoreThreshold: 0.5,
      nmsRadius: 20,
      detectionType: 'single',
      inputResolution: 257,
      multiplier: 0.75,
      quantBytes: 2,
  };

  // assign poseNet
  poseNet = ml5.poseNet(video, options, modelReady);
  
  // This sets up an event that listens to 'pose' events
  poseNet.on('pose', function (results) {
  poses = results;
  })
}

function modelReady() {
  select('#status').html('Model Loaded');
}


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
      for (let j = 0; j < pose.keypoints.length; j++) {
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

// A function to draw the skeletons
function drawSkeleton() {
  // Loop through all the skeletons detected
  if (poses.length > 0){
    for (let i = 0; i < poses.length; i++) {
      let skeleton = poses[i].skeleton;
      // For every skeleton, loop through all body connections
      for (let j = 0; j < skeleton.length; j++) {
        let partA = skeleton[j][0];
        let partB = skeleton[j][1];
        stroke(255, 0, 0);
        line(partA.position.x, partA.position.y, partB.position.x, partB.position.y);
      }
    }
  }
}

// Extract keypoints
var a = setInterval(extractPoses, 200);
function extractPoses(){
  if (poses.length > 0){
    console.log("compare:")
    console.log(poses[0].pose.keypoints);
    console.log(poses_seq[poses_seq.length-1]);
    if (JSON.stringify(poses[0].pose.keypoints) == JSON.stringify(poses_seq[poses_seq.length-1])){
      console.log("same");
      clearInterval(a);
      console.log(poses_seq);

      // Save keypoints to json file
      // var obj = poses_seq;
      var data = "text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(poses_seq));

      var b = document.createElement('a');
      b.href = 'data:' + data;
      b.download = 'data.json';
      b.innerHTML = 'download JSON';

      var container = document.getElementById('download');
      container.appendChild(b);
    } 
    else {
      poses_seq.push(poses[0].pose.keypoints);
    }
  }
}

