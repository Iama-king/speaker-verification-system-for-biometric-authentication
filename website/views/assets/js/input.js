//initialize elements we'll use
const user = document.getElementById('unam')
const recordButto = document.getElementById('recordButto');
const stopButto = document.getElementById("stopButto");
const recordedAudioContaine = document.getElementById('recordedAudioContaine');
const saveAudioButto = document.getElementById('saveButto');

let chunk = []; //will be used later to record audio
let mediarecorder = null; //will be used later to record audio
let audioblob = null; //the blob that will hold the recorded audio

recordButto.addEventListener('click', recor);
stopButto.addEventListener('click', stopre);
saveAudioButto.addEventListener('click', saveRecordin);

function mediaRecorderDataAvailabl(e) {
    chunk.push(e.data);
}
function mediaRecorderSto () {
    //check if there are any previous recordings and remove them
    if (recordedAudioContaine.firstElementChild.tagName === 'AUDIO') {
      recordedAudioContaine.firstElementChild.remove();
    }
    //create a new audio element that will hold the recorded audio
    const audioElm = document.createElement('audio');
    audioElm.setAttribute('controls', ''); //add controls
    //create the Blob from the chunks
    audioblob = new Blob(chunk, { type: 'audio/wav' });
    const audioURL = window.URL.createObjectURL(audioblob);
    audioElm.src = audioURL;
    //show audio
    // recordedAudioContainer.insertBefore(audioElm, recordedAudioContainer.firstElementChild);
    // recordedAudioContainer.classList.add('d-flex');
    // recordedAudioContainer.classList.remove('d-none');
    //reset to default
    mediarecorder = null;
    chunk = [];
  }
function recor() {
    if(user.value==""){
      alert("Please enter the username");
      return;
    }
  
    //TODO start recording
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Your browser does not support recording!');
        return;
    }
    if (!mediarecorder) {
      recordButto.style.color="#ffffff"
      recordButto.style.background= '#bdbdbd'
      recordButto.disabled=true;
        // start recording
        alert('Recording started');
        navigator.mediaDevices.getUserMedia({
          audio: true,
        })
          .then((stream) => {
            
            mediarecorder = new MediaRecorder(stream);
            mediarecorder.start();

            mediarecorder.ondataavailable = mediaRecorderDataAvailabl;
            mediarecorder.onstop = mediaRecorderSto;
            setTimeout(function() {
              mediarecorder.stop();
              alert('Recording Stopped');
              
              // Stop the media stream from the microphone
              var tracks = stream.getTracks();
              tracks.forEach(function(track) {
                stopButto.disabled=false;
                saveAudioButto.disabled=false;
                stopButto.style.background = "#dd2424";
                saveAudioButto.style.background="#dd2424";
        
                track.stop();
              });
            }, 11000);
           
          })
          .catch((err) => {
            alert(`The following error occurred: ${err}`);
          });
        
      }

}
function stopre(){

  stopButto.style.color="#ffffff"
  stopButto.style.background= '#bdbdbd';
  stopButto.disabled=true;
  saveAudioButto.style.color="#ffffff"
  saveAudioButto.style.background= '#bdbdbd'
  saveAudioButto.disabled=true;
  audioblob=null;
  alert('Discarded audio')
  window.location.reload()
} 
function saveRecordin () {
  document.getElementById("login").disabled=false;
  if(audioblob!=null){ 
    saveAudioButto.style.color="#ffffff"
    saveAudioButto.style.background= '#bdbdbd'
    saveAudioButto.disabled=true;
    stopButto.style.color="#ffffff"
    stopButto.style.background= '#bdbdbd';
    stopButto.disabled=true;
    //the form data that will hold the Blob to upload
    const formData = new FormData();
    //add the Blob to formData
    formData.append('validation', audioblob, user.value+'.wav');
    //send the request to the endpoint
    fetch('/record', {
      method: 'POST',
      body: formData
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