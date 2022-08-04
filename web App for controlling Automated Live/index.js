const express = require("express");
const mqtt = require("mqtt");
const fs = require("fs");

const bodyParser = require("body-parser");

const app = express();

const host = "ajpqtrpkadas99.cricheroes.in";
const port = "8883";
// const clientId = `mqtt_${Math.random().toString(16).slice(3)}`; // genrating random id
// const options = {clientId: clientId, clean: false, reconnectPeriod: 1}

const connectUrl = `mqtt://${host}:${port}`;

const client = mqtt.connect(connectUrl, { clientId: "rishi_form_node" });
// console.log("Is_connected : " + client.connected);
// client.on("connect", () => console.log("connected to mqtt broker"));

const topic = "stream-info";

app.set("view engine", "ejs");

// middleware
app.use(bodyParser.urlencoded({ extended: false }));

// route
// home nav
app.get("/", (req, res) => {
  res.render("home", {
    pageName: "Raspi Controller",
    path: "/",
  });
});
// {"isLive":false,"stream_key":"","match_id":"","stream_fps":"","stream_resolution":""}

// start-stream nav
app.get("/start-stream", (req, res) => {
  // read data from file to render the ejs
  let stream_data = fs.readFileSync("stream_config.txt", { flag: "r" });
  stream_data = JSON.parse(stream_data.toString());
  console.log(stream_data);

  res.render("start_stream", {
    pageName: "Raspi Stream Starter",
    stream_data: stream_data,
    path: "/start-stream",
  });
});

// start strea go live button
app.post("/start-stream", (req, res) => {
  let stream_config = {
    isLive: true,
    stream_key: req.body.stream_key,
    match_id: req.body.match_id,
    stream_fps: req.body.stream_fps,
    stream_resolution: req.body.stream_resolution,
    stream_link: "https://www.youtube.com/embed" + req.body.stream_link.slice(req.body.stream_link.lastIndexOf('/'))
  };
  // saving stream config to file
  fs.writeFile("stream_config.txt", JSON.stringify(stream_config), (err) => {
    if (err) console.log(err);
    console.log("stream data saved");
  });
  console.log(JSON.stringify(stream_config));

  if (client.connected) {
    console.log("connected with Mqtt and sending stream config to raspi");
    // client.subscribe([topic], () => {
    //   console.log(`Subscribe to topic '${topic}'`);
    // });

    client.publish(topic, JSON.stringify(stream_config), () => {
      console.log(`data sent to raspi`);
    });
  } else console.log("not connected");

  res.redirect("/");
});

// end-stream nav
app.get("/end-stream", (req, res) => {
  // read data from file to render the ejs
  let stream_data = fs.readFileSync("stream_config.txt", { flag: "r" });
  stream_data = JSON.parse(stream_data.toString());
  console.log(stream_data);

  res.render("end_stream", {
    pageName: "Raspi Stream Ender",
    stream_data: stream_data,
    path: "/end-stream",
  });
});

app.post("/end-stream", (req, res) => {
  console.log("stream ending soon");
  let stream_data = {
    isLive: false,
    stream_key: "",
    match_id: "",
    stream_fps: "",
    stream_resolution: "",
    stream_link: ""
  };
  fs.writeFile("stream_config.txt", JSON.stringify(stream_data), (err) => {
    if (err) console.log(err);
    console.log("stream data saved");
  });

  if (client.connected) {
    console.log("connected with raspi for stoping stream");
    // client.subscribe([topic], () => {
    //   console.log(`Subscribe to topic '${topic}'`);
    // });

    client.publish(topic, JSON.stringify(stream_data), () => {
      console.log(`data sent to raspi`);
    });
  } else console.log("not connected");

  res.redirect("/");
});

app.get("/show-live", (req, res) => {
  let stream_data = fs.readFileSync("stream_config.txt", { flag: "r" });
  stream_data = JSON.parse(stream_data.toString());
  // console.log(stream_data);
  res.render("yt", {
    pageName: "Raspi Live Stream,",
    stream_data: stream_data,
    path: "/show-live"
  })
})
  

app.listen(3000, () => console.log("server started running on 3000"))
