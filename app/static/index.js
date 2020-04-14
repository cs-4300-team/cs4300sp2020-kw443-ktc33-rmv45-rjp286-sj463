const app = new Vue({
  el: '#app',
  data: {
    input: 'Input:',
    output: 'Output:'
  },
})

var inputSet = new Set();
function addInput() {
  // https://stackoverflow.com/questions/17650776/add-remove-html-inside-div-using-javascript
  // source used to add/remove elements
  var new_input = document.getElementById("input_text").value;
  if (inputSet.has(new_input) == false && new_input != "" && new_input != "Enter input." && new_input.includes("https://open.spotify.com/playlist/")) {

    var data = "link=" + new_input + "&get_playlist=true";
    fetch('/', {
      method: 'POST',
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: data
    })
      .then(res => res.json())
      .then(info => {
        // let string_output = "";
        // this.outputs = songs;
        // for (let i = 0; i < this.outputs.length; i++) {
        //   string_output = string_output + " <br /> " + this.outputs[i];
        // }
        // document.getElementById("output_label").innerHTML = "Outputs:";
        // document.getElementById("response").innerHTML = string_output;
        inputSet.add(new_input);
        const div = document.createElement('div');
        div.className = 'row';
        div.innerHTML = `<img src=url(` + info['images'] + `)></img>
       <span>`+ info['name'] + `</span>
        <input id="`+ new_input + `" type="button" value="X" onclick="removeRow(this)" />`;
        document.getElementById('input_list').appendChild(div);
        console.log(info);
        document.getElementById("error_message").style.display = 'none';
      })
      .catch(e => {
        console.log("ERROR");
        document.getElementById("error_message").style.display = 'block';
        document.getElementById("error_message").innerHTML = "Sorry, your playlist link appears to be invalid. Please try another link."
      })
  }
  document.getElementById('input_text').value = "";
  document.getElementById('input_text').placeholder = "Add to Your Playlists.";
}

function removeRow(input) {
  document.getElementById('input_list').removeChild(input.parentNode);
  inputSet.delete(input.id);
}

function output() {
  if (inputSet.size > 0) {
    var data = "";
    inputSet.forEach((item) => {
      if (data === "") {
        data += ("link=" + item);
      }
      else {
        data += ("&link=" + item);
      }
    })
    data += ("&get_playlist=false");
    fetch('/', {
      method: 'POST',
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: data
    })
      .then(res => res.json())
      .then(songs => {
        let string_output = "";
        song_outputs = songs;
        for (let i = 0; i < song_outputs.length; i++) {
          string_output += " <br /> " + song_outputs[i].name;
          artist_output = "";
          for (let j = 0; j < song_outputs[i]['artists'].length; j++) {
            if (j > 0) {
              artist_output += ",";
            }
            artist_output += " " + song_outputs[i]['artists'][j]['name'];
          }
          string_output += artist_output;
        }
        document.getElementById("error_message").style.display = 'none';
        document.getElementById("output_label").innerHTML = "Outputs:";
        document.getElementById("response").innerHTML = string_output;
        // console.log(songs);
      })
      .catch(e => {
        console.log("ERROR")
        document.getElementById("error_message").style.display = 'block';
        document.getElementById("error_message").innerHTML = "Sorry, it looks like something went wrong."
      })
    console.log("done");
  }
}