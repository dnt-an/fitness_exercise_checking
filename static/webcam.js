let video;
let interval;

let poseNet;
let poses = [];

// set some options for posenet model
let options = {
  architecture: 'MobileNetV1', // MobileNetV1, ResNet50
  imageScaleFactor: 0.8, //  A number between 0.2 and 1. Set this number lower to scale down the image and increase the speed when feeding through the network at the cost of accuracy.
  outputStride: 16, // (8, 16, 32) The smaller the value, the larger the output resolution, and more accurate the model at the cost of speed
  flipHorizontal: false,
  minConfidence: 0.5,
  maxPoseDetections: 3,
  scoreThreshold: 0.5,
  nmsRadius: 20,
  detectionType: 'single',
  inputResolution: 417, // (161, 193, 257, 289, 321, 353, 385, 417, 449, 481, 513, 801) The larger the value, the more accurate the model at the cost of speed
  multiplier: 0.75,  // (0.5, 0.75, 1, 1.01) The larger the value, the larger the size of the layers, and more accurate the model at the cost of speed
  quantBytes: 2 // (4, 2, 1)
};

function setup() {
  var canvas = createCanvas(800, 600);
  canvas.parent('sketch-holder');
  let constraints = {
    video: {
      optional: [{ maxFrameRate: 1000 }]
    },
    audio: false
  };
  video = createCapture(VIDEO);
  video.volume(0);
  
  // set the video size to the size of the canvas (canvas's size will effect the keypoints coordinate)
  video.size(width, height);
  
  // Hide the video element, and just show the canvas
  video.hide();
  // assign poseNet
  poseNet = ml5.poseNet(video, options, modelReady);

   // This sets up an event that fills the global variable "poses"
  // with an array every time new poses are detected
  poseNet.on('pose', function (results) {
    poses = results;
    // console.log(poses)
  });
}

function startTraining(){
  let starting_btn = document.getElementsByClassName("starting_training_btn")[0];
  starting_btn.style.display = "none";
  let stopping_btn = document.getElementsByClassName("stopping_training_btn")[0];
  stopping_btn.style.display = "block";
  setTimeout(function(){
    interval = setInterval(sendData, 125);
  }, 1000); 
}

function stopTraining(){  
  let starting_btn = document.getElementsByClassName("starting_training_btn")[0];
  starting_btn.style.display = "block";
  let stopping_btn = document.getElementsByClassName("stopping_training_btn")[0];
  stopping_btn.style.display = "none";
  clearInterval(interval);
  $('ResultModal').modal('show');
}

function sendData() {
  let queryString = window.location.search;
  //console.log(queryString);
  let urlParams = new URLSearchParams(queryString);
  let type_exercise = urlParams.get('type')
  //console.log(type_exercise);

  if (poses.length>0){
      if (poses[0].pose.score > 0.05){
        let json_data = {'data-uri': poses[0].pose.keypoints,
                          'type-exercise': type_exercise}
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
        document.getElementById("cond1").innerHTML = res.cond1;
        document.getElementById("cond2").innerHTML = res.cond2;
        document.getElementById("mistake_count").innerHTML = res.mistake_count;
        document.getElementById("success_count").innerHTML = res.success_count;
        document.getElementById("feedback").innerHTML = res.feedback;
        document.getElementById("modal_mistake_count").innerHTML = res.mistake_count;
        document.getElementById("modal_success_count").innerHTML = res.success_count;
        document.getElementById("modal_feedback").innerHTML = res.feedback;

        if (res.sound_file=='excellent.mp3'){
          document.getElementById("audioExcellent").play();
          console.log("Playing sound now!");
        } else if (res.sound_file=='excellent2.mp3'){
          document.getElementById("audioExcellent2").play();
          console.log("Playing sound now!");
        } else if (res.sound_file=='excellent3.mp3'){
          document.getElementById("audioExcellent3").play();
          console.log("Playing sound now!");
        } else if (res.sound_file=='excellent4.mp3'){
          document.getElementById("audioExcellent4").play();
          console.log("Playing sound now!");
        } else if (res.sound_file=='bicep_curls_mistake1.mp3'){
          document.getElementById("audioBicepCurls1").play();
          console.log("Playing sound now!");
        } else if (res.sound_file=='bicep_curls_mistake2.mp3'){
          document.getElementById("audioBicepCurls2").play();
          console.log("Playing sound now!");
        } else if (res.sound_file=='front_raise_mistake1.mp3'){
          document.getElementById("audioFrontRaise1").play();
          console.log("Playing sound now!");
        } else if (res.sound_file=='front_raise_mistake2.mp3'){
          document.getElementById("audioFrontRaise2").play();
          console.log("Playing sound now!");
        } else if (res.sound_file=='lateral_raise_mistake1.mp3'){
          document.getElementById("audioLateralRaise1").play();
          console.log("Playing sound now!");
        } else if (res.sound_file=='lateral_raise_mistake2.mp3'){
          document.getElementById("audioLateralRaise2").play();
          console.log("Playing sound now!");
        } else if (res.sound_file=='squat_mistake1.mp3'){
          document.getElementById("audioSquat1").play();
          console.log("Playing sound now!");
        } else if (res.sound_file=='squat_mistake2.mp3'){
          document.getElementById("audioSquat2").play();
          console.log("Playing sound now!");
        }
      })
    }
  }
}


function modelReady() {
  select('#status').html('Model Loaded');
}

function draw() {
  background(200)
  image(video, 0, 0, width, height);

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
        // A keypoint is an object describing a body part (like rightArm or leftShoulder)
        let keypoint = pose.keypoints[j];
        // Only draw an ellipse is the pose probability is bigger than 0.6
        if (keypoint.score > 0.5) {
          fill(250,182,23);
          stroke(20);
          strokeWeight(2);
          ellipse(keypoint.position.x, keypoint.position.y, 12, 12);
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
        if (![0,5,10,11].includes(j)){
        let partA = skeleton[j][0];
        let partB = skeleton[j][1];
        stroke(255);
        strokeWeight(2);
        line(partA.position.x, partA.position.y, partB.position.x, partB.position.y);
        }
      }
    }
  }
}




