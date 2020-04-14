// var inputSet = new Set();
function addInput() {
  // https://stackoverflow.com/questions/17650776/add-remove-html-inside-div-using-javascript
  // source used to add/remove elements

  const new_input = this.input // this.input "models" the input from html
  // var new_input = document.getElementById("input_text").value;

  if(new_input) { // this checks for empty string
    // todo: better input validation
    this.inputSet.add(new_input); // dont need to check for membership since it's a set
  }
  /* Equivalent to: */
  // if (inputSet.has(new_input) == false && new_input != "" && new_input != "Enter input.") {
  //   inputSet.add(new_input);
  //   const div = document.createElement('div');
  //   div.className = 'row';
  //   div.innerHTML = `
  //  <span>`+ new_input + `</span>
  //   <input id="`+ new_input + `" type="button" value="X" onclick="removeRow(this)" />
  // `;
  //   document.getElementById('input_list').appendChild(div);
  // }

  // this works due to modeling:
  this.input = '';
  /* Equivalent to: */
  // document.getElementById('input_text').value = "";
  // document.getElementById('input_text').placeholder = "Add to Your Playlists.";
}

function output() {
  // var data = "link=https://open.spotify.com/playlist/5hOxxrUnRYpf6XVScyjF0Y&link=https://open.spotify.com/playlist/48KXkzzA9xkonptFgWx1a9"
  const data = [...this.inputSet].map(link => `link=${link}`).join('&')

  // let xhr = new XMLHttpRequest();
  // xhr.open("POST", "/", true);
  // xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  // xhr.send(data);
  // xhr.onload = function () {
  //   if (xhr.status != 200) { // analyze HTTP status of the response
  //     alert(`Error ${xhr.status}: ${xhr.statusText}`); // e.g. 404: Not Found
  //   } else { // show the result
  //     alert(`Done, got ${xhr.response}`); // responseText is the server
  //   }
  // };
  // console.log("blah");
  // console.log("done");
  // document.getElementById("output_text").innerHTML = "Outputs:";
  /* Using modern fetch api which provides a promise:
  https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch */
  fetch('/', {
    method: 'POST',
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: data
  })
    .then(res => res.json())
    .then(songs => {
      this.outputs = songs;
    })
    .catch(e => {
      console.error(e);
      // error handle here!
    })
}

const app = new Vue({
  el: '#app',
  data: {
    input: '',
    inputSet: new Set(['https://open.spotify.com/playlist/5hOxxrUnRYpf6XVScyjF0Y', 
      'https://open.spotify.com/playlist/48KXkzzA9xkonptFgWx1a9']),
    outputs: [],
  },
  methods: {
    addInput,
    removeRow(input) {
      this.inputSet.delete(input);
      // have to do because of set
      this.$forceUpdate();
    },
    output
  },
  computed: {
    stringOutput() {
      return this.outputs.join("\n")
    }
  }
});

// function removeRow(input) {
//   document.getElementById('input_list').removeChild(input.parentNode);
//   inputSet.delete(input.id);
// }
