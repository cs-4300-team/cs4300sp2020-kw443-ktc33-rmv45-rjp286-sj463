// var inputSet = new Set();
function addInput() {
  // https://stackoverflow.com/questions/17650776/add-remove-html-inside-div-using-javascript
  // source used to add/remove elements

  let new_input = this.input // this.input "models" the input from html
  // var new_input = document.getElementById("input_text").value;
  try {
    const url = new URL(this.input)
    new_input = url.origin + url.pathname;
  } catch (e) {
    this.error_message = `Error parsing input. Please format it as a link to a playlist`;
  }

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

        this.updateHash();
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
  this.stuckPopup = false;

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

const examplesString = `37i9dQZF1DX9s3cYAeKW5d=Hip-Hop%20Workout%20Mix&%3E%3E%3E37i9dQZF1DX48TTZL62Yht=Hip-Hop%20Favourites&%3E%3E%3E28ONiLZsrlTPUYxmC7ZJ0f=Hip-Hop%20Hits&%3E%3E%3E37i9dQZF1DX8WMG8VPSOJC=Country%20Kind%20of%20Love`

const app = new Vue({
  el: '#app',
  data: {
    input: '',
    inputSet: {},
    outputs: [],
    examples: decodeURIComponent(examplesString)
      .split('&>>>')
      .map(i => i.split(/=(.+)/))
      .map(([id, name]) => ({id, name})),
    error_message: '',
    stuckPopup: false
  },
  methods: {
    addInput,
    removeRow(input) {
      delete this.inputSet[input];
      // have to do because of set
      this.$forceUpdate();
      this.updateHash();
    },
    output,
    image(song) {
      if(!song || !song.images || song.images.length === 0) {
        return 'static/not_found.png'
      }
      // use spread here to avoid mutating song
      try {
        const sorted = [...song.images].sort((a, b) => b.height - a.height);
        return sorted[sorted.length - 1].url
      } catch (e) {
        return 'static/not_found.png'
      }
    },
    updateHash() {
      const is = this.inputSet
      let newHash = Object.keys(is)
        .map(k => [new URL(k).pathname.split('/').pop(), is[k]])
        .map(([id, name]) => `${id}=${name}`).join('&>>>')
      window.location.hash = `#${newHash}`
    },
    setExample(example) {
      this.input = 'https://open.spotify.com/playlist/' + example.id
    }
  },
  computed: {
    stringOutput() {
      return this.outputs.join("\n")
    }
  },
  mounted() {
    const hash = decodeURIComponent(window.location.hash);
    if(!hash || hash.length == 0) {
      return;
    }
    try {
      const inputs = hash.substring(1).split('&>>>').map(i => i.split(/=(.+)/))
      for(let [url, name] of inputs) {
        this.inputSet['https://open.spotify.com/playlist/' + url] = decodeURIComponent(name)
      }
      this.$forceUpdate();
    } catch (e) {
      window.location.hash = ''
    }

  }
});
