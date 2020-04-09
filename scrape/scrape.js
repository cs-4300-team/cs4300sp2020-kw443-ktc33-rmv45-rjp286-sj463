// scrape spotify API for user names by traversing a users followers/following
// some sensitive endpoints and headers are censored and must be scaped
// (don't want to publicize private API requests)
const fs = require('fs');

const PROXIES_FILE = './proxies.txt';

const got = require('got');
const tunnel = require('tunnel');

const TIMEOUT_MS = 10000;
const timeout = {
    lookup: TIMEOUT_MS,
    connect: TIMEOUT_MS,
    secureConnect: TIMEOUT_MS,
    socket: TIMEOUT_MS,
    response: TIMEOUT_MS,
    send: TIMEOUT_MS,
    request: TIMEOUT_MS
}

async function following(type, proxy, token, id) {
    const [userOrHost, passOrPort, maybeHost, maybePort] = proxy.split(":");
    
    const user = maybeHost && userOrHost;
    const pass = maybeHost && passOrPort;

    const proxyAuth = (user && pass && `${user}:${pass}`) || undefined;

    const host = (user && maybeHost) || userOrHost;
    const port = (user && maybePort) || passOrPort;

    const agent = tunnel.httpsOverHttp({
        proxy: {
            host,
            port,
            proxyAuth
        }
    });


    function randomEmail() {
        return `spotify${Math.floor(Math.random() * 50000)}`;
    }

    // can be scraped by going to a users profile and going to their followers/following
    const res = await got(`FOLLOWERS_FOLLOWING_URL/${id}/${type}`, {
        headers: {
            // can be scraped from the same request
        },
        agent,
        timeout
    });

    const result = JSON.parse(res.body);
    
    return result;
}

const users = [['USER_ID_HERE_TO_START_FROM', 'following']]
const done = fs.readFileSync('output.txt', 'utf8').split('\n').map(u => u.trim());
const token = 'BEARER_TOKEN_HERE' // can be scraped from a request the app makes, apparently valid for 1 hour

function delay(time) {
    return new Promise((res) => setTimeout(res, time));s
}

const PARALLEL_COUNT = 5;

fs.readFile(PROXIES_FILE, 'utf8', async (err, data) => {
    if(err) {
        console.error(`Error reading proxies file!`.red);
        return;
    }

    const proxies = data.split(/[\r\n]+/g).filter(s => s.length !== 0 && s.includes(':'));

    const output = fs.createWriteStream('output.txt', {
        flags: 'a'
    });

    function doIt(endQuick = false) {
        return new Promise(async (resolve, reject) => {
            while(users.length > 0) {
                let proxy = proxies[Math.floor(Math.random()*proxies.length)];
                try {
                    let [user, type] = users.shift();
                    if(!user) break;
                    const f = await following(type, proxy, token, user);
                    for(let follow of f.profiles) {
                        try {
                            if(!follow.user_uri) continue;
                            let userId = follow.user_uri.split("user:").pop();
                            let type =  follow.followers_count > follow.following_count ? 'followers' : 'following';
                            console.log(userId);
                            if(userId && !done.includes(userId)) {
                                done.push(userId);
                                users.push([userId, type]);
                                output.write(userId + '\n');
                            }
                        } catch (e) {
                            console.log(e)
                        }
                    }
                } catch (e) {
                    console.log(e);
                }
                if(endQuick) {
                    break;
                }
                await delay(2000);
            }
            resolve();
        })
    }

    // this is to seed initially
    await doIt(true);

    let tasks = [];
    for(let i = 0; i < PARALLEL_COUNT; i++) {
        tasks.push(doIt());
    }
    // this will probably never resolve
    await Promise.all(tasks);

    output.close();
});