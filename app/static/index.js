// var inputSet = new Set();
function addInput() {
  // https://stackoverflow.com/questions/17650776/add-remove-html-inside-div-using-javascript
  // source used to add/remove elements

  const new_input = this.input // this.input "models" the input from html
  // var new_input = document.getElementById("input_text").value;

  if (new_input &&
    new_input.includes("https://open.spotify.com/playlist/")) { // this checks for empty string

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
        this.inputSet[new_input] = info['name'];

        this.error_message = '';
        this.$forceUpdate();
      })
      .catch(e => {
        console.log("ERROR");
        this.error_message = 'Sorry, your playlist link appears to be invalid. Please try another link.';
      })
  }
  this.input = '';
}

function output() {
  // var data = "link=https://open.spotify.com/playlist/5hOxxrUnRYpf6XVScyjF0Y&link=https://open.spotify.com/playlist/48KXkzzA9xkonptFgWx1a9"
  let data = (Object.keys(this.inputSet)).map(link => `link=${link}`).join('&')
  data += "&get_playlist=false";

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
      this.error_message = '';
    })
    .catch(e => {
      console.log("ERROR");
      this.error_message = 'Sorry, there appears to be a problem.';
      // error handle here!
    })
}

const app = new Vue({
  el: '#app',
  data: {
    input: '',
    inputSet: {},
    outputs: [],
    error_message: ''
  },
  methods: {
    addInput,
    removeRow(input) {
      delete this.inputSet[input];
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