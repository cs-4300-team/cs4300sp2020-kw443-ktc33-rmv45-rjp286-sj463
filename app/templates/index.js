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
  if (inputSet.has(new_input) == false && new_input != "" && new_input != "Enter input.") {
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
  console.log("done");
  document.getElementById("output_text").innerHTML = "Outputs:"
}