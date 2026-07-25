
//initialize elements we'll use
const username = document.getElementById('uname')
const email = document.getElementById('ename')
const recordButton = document.getElementById('recordButton');
const stopButton = document.getElementById("stopButton");
const recordedAudioContainer = document.getElementById('recordedAudioContainer');
const saveAudioButton = document.getElementById('saveButton');
var gumstream;
let chunks = []; //will be used later to record audio
let mediaRecorder = null; //will be used later to record audio
let audioBlob = null; //the blob that will hold the recorded audio
let k=true;
recordButton.addEventListener('click', record);
stopButton.addEventListener('click', stoprec);
saveAudioButton.addEventListener('click', saveRecording);

function mediaRecorderDataAvailable(e) {
    chunks.push(e.data);
}
function mediaRecorderStop () {
    //check if there are any previous recordings and remove them
    if (recordedAudioContainer.firstElementChild.tagName === 'AUDIO') {
      recordedAudioContainer.firstElementChild.remove();
    }
    //create a new audio element that will hold the recorded audio
    const audioElm = document.createElement('audio');
    audioElm.setAttribute('controls', ''); //add controls
    //create the Blob from the chunks
    audioBlob = new Blob(chunks, { type: 'audio/wav' });
    const audioURL = window.URL.createObjectURL(audioBlob);
    audioElm.src = audioURL;
    //show audio
    // recordedAudioContainer.insertBefore(audioElm, recordedAudioContainer.firstElementChild);
    // recordedAudioContainer.classList.add('d-flex');
    // recordedAudioContainer.classList.remove('d-none');
    //reset to default
    mediaRecorder = null;
    chunks = [];
  }
function record() {
    
    // function submitForm() {
  
    // }

    // Enable the login button only when the username field has a value
    // userInput.addEventListener('input', function() {
    //     signin.disabled = userInput.value && email.value;
    // });
    
        if (email.value == "" || username == "") {
            alert("Please enter the username and email");
            return;
 
        } 
        
  
    //TODO start recording
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Your browser does not support recording!');
        return;
    }
    if (!mediaRecorder) {
      recordButton.style.color="#ffffff"
      recordButton.style.background= '#bdbdbd'
      recordButton.disabled=true;
        // start recording
        alert('Recording started');
        navigator.mediaDevices.getUserMedia({
          audio: true,
        })
          .then((stream) => {
            gumstream = stream;
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            mediaRecorder.ondataavailable = mediaRecorderDataAvailable;
            mediaRecorder.onstop = mediaRecorderStop;
            setTimeout(function() {
              mediaRecorder.stop();
              alert('Recording Stopped');
              
              // Stop the media stream from the microphone
              var tracks = stream.getTracks();
              tracks.forEach(function(track) {
                stopButton.disabled=false;
                saveAudioButton.disabled=false;
                stopButton.style.background = "#dd2424";
                saveAudioButton.style.background="#dd2424";
        
                track.stop();
              });
            }, 11000);
           
          })
          .catch((err) => {
            alert(`The following error occurred: ${err}`);
          });
        
      }
      

}
function stoprec(){

  stopButton.style.color="#ffffff"
  stopButton.style.background= '#bdbdbd';
  stopButton.disabled=true;
  saveAudioButton.style.color="#ffffff"
  saveAudioButton.style.background= '#bdbdbd'
  saveAudioButton.disabled=true;
  audioBlob=null;
  alert('Discarded audio!');
  window.location.reload();
} 
function saveRecording () {
  document.getElementById("sub").disabled=false;
  
  if(audioBlob!=null){ 
    saveAudioButton.style.color="#ffffff"
    saveAudioButton.style.background= '#bdbdbd'
    saveAudioButton.disabled=true;
    stopButton.style.color="#ffffff"
    stopButton.style.background= '#bdbdbd';
    stopButton.disabled=true;
    //the form data that will hold the Blob to upload
    const formData = new FormData();
    //add the Blob to formData
    formData.append('Enroll', audioBlob, username.value+'.wav');
    //send the request to the endpoint
    fetch('/record', {
      method: 'POST',
      body: formData,
      
    })
    .then((response) => response.json())
    .then(() => {
      alert("Your recording is saved");
      //reset for next recording
      // resetRecording();
      //TODO fetch recordings
    })
    .catch((err) => {
      console.error(err);
      alert("An error occurred, please try again later");
      //reset for next recording
      // resetRecording();
    })
  }
  
  
}
const login=document.getElementById('login');

login.addEventListener("click", async (e) => {

  const res = await fetch("/dat")
  const data = await res.json();
  console.log(data.result);
  if (data.result === 'yes\r\n') {
      window.location.href = '/new.html';
  } else {
      console.log('Error: Invalid result value');
      alert("Try again");
      window.location.reload();
  }

});




