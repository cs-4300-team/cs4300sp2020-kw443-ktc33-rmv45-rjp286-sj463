const got = require('got');
const fs = require('fs');
const songs = [];
const words = {}

const top_songs = JSON.parse(fs.readFileSync('top_songs.json'), 'utf8')

async function scrapeTop() {
    let out = [];
    let done = 0;
    for(let song of top_songs) {
        const q = song.name + " " + song.artist;
        console.log(q)

        const res = await got(`https://api.pushshift.io/reddit/comment/search/`, {
            searchParams: {
                q
            },
            responseType:'json'
        });

        // console.log(res.body.data);
        let data = {
            'name': song.name,
            'artist': song.artist,
            'comments': res.body.data.map(d => d.body)
        }
        for(let comment of res.body.data.map(d => d.body)) {
            for(let word of comment.split(/([^\w]+)/g)) {
                if(!words[word]) {
                    words[word] = 1
                } else {
                    words[word] ++;
                }
            }
        }
        out.push(data);
        done++;
        if(done >= 100) {
            break;
        }
    }
    fs.writeFileSync('scraped_comments.json', JSON.stringify(out, null, 4))

    console.log(Object.keys(words)
        .map(word => ({word, count: words[word]}))
        .sort((a, b) => b.count - a.count))
}

scrapeTop();