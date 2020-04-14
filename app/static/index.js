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
    inputSet.add(new_input);
    const div = document.createElement('div');
    div.className = 'row';
    div.innerHTML = `
   <span>`+ new_input + `</span>
    <input id="`+ new_input + `" type="button" value="X" onclick="removeRow(this)" />
  `;
    document.getElementById('input_list').appendChild(div);
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
    // var data = "link=https://open.spotify.com/playlist/5hOxxrUnRYpf6XVScyjF0Y&link=https://open.spotify.com/playlist/48KXkzzA9xkonptFgWx1a9"
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "http://0.0.0.0:5000", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.send(data);
    xhr.onload = function () {
      if (xhr.status != 200) { // analyze HTTP status of the response
        alert(`Error ${xhr.status}: ${xhr.statusText}`); // e.g. 404: Not Found
      } else { // show the result
        let output = JSON.parse(xhr.response);
        let string_output = "";
        document.getElementById("output_label").innerHTML = "Outputs:";
        for (let i = 0; i < output.length; i++) {
          string_output = string_output + " <br /> " + output[i];
        }
        document.getElementById("response").innerHTML = string_output;
        // alert(`Done, got ${xhr.response}`); // responseText is the server
      }
    };
    console.log("done");
  }
}