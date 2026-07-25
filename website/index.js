const path = require('path');
const express = require("express");
const admin = require("firebase-admin");
const {spawn} = require('child_process');
const multer = require('multer');
var dataToSend;
var username_data;


const storage = multer.diskStorage({
  destination(req, file, cb) {
    const fs = require('fs');

    const folderName = path.join("C:/Users/sanja/PycharmProjects/SpeakerRecognition_tutorial/website",file.fieldname,(file.originalname).split(".")[0]);
    username_data=(file.originalname).split(".")[0];
    try {
      if (!fs.existsSync(folderName)) {
        fs.mkdirSync(folderName);
      }
    } catch (err) {
      console.error(err);
    }
    
    //const dir = file.fieldname;
    cb(null, folderName);
  },
   filename(req, file, cb) {
   const fileNameArr = file.originalname;
   cb(null, `${fileNameArr}`);
  },
});



const upload = multer({ storage });

//auth
const bodyParser=require('body-parser')
const ejs=require('ejs');
const app = express(); 
const port = process.env.PORT || 3008;
app.use(bodyParser.json())

app.engine('html',require("ejs").renderFile);
app.get("/signup",function(req,res){
  res.render("index.html");
})

app.get("/profile", function (req, res) {
  res.render("new.html");
});



app.use(express.static('views/assets'));
app.use(express.static('Enroll'));
app.use(express.static('validation'));
app.use(express.static('views'))
app.get('/',(req,res)=>{
  res.sendFile(path.join(__dirname, 'views/index.html'));
  res.sendFile(path.join(__dirname,'views/new.html'));
});

const activatecmd='conda activate tf';
const pythoncmd = 'python';
const cmd='${pythoncmd}'
app.get('/dat',(req,res)=>{

  const python = spawn('conda activate tf & python ',['C:/Users/sanja/PycharmProjects/SpeakerRecognition_tutorial/test.py', username_data ], {shell:true});
  python.stdout.on('data' , function (data) {
   dataToSend = data.toString();
   console.log(dataToSend);
  });
  python.on('close', (code) => {
  let dat = {result:dataToSend};
  res.json(dat);

  }); 
}); 
app.post('/record', upload.any(), (req, res) => res.json({ success: true }));

// app.post('/record', upload.single('validation'), (req, res) => res.json({ success: true }));
app.listen(port, () => {
  console.log(`App listening at http://localhost:${port}`);
});