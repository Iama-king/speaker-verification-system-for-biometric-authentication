const express = require('express');
const bodyParser = require('body-parser');
const MongoClient = require('mongodb').MongoClient;
const bcrypt = require('bcryptjs');
const app = express();
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.json());
const url = 'mongodb://localhost:27017';
const dbName = 'mydb';

MongoClient.connect(url, { useUnifiedTopology: true }, (err, client) => {
  if (err) return console.log(err);
  console.log('Connected to MongoDB');

  const db = client.db(dbName);
  db.createCollection('users',function(err,res){
    if(err) throw err;
    console.log("Collection created");
  })
  const users = db.collection('users');
  
});
