// register a spotify account using mobile api
// some sensitive endpoints, headers, and request bodies are censored and must be scaped
// (don't want to publicize private API requests)

const fs = require('fs');

const CATCHALL = 'INSERT_CATCHALL_DOMAIN_HERE'
const PROXIES_FILE = './proxies.txt';

const got = require('got');
const tunnel = require('tunnel');

async function register(proxy, catchall, password) {
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

    const email = `${randomEmail()}@${catchall}`;

    // Scrape the endpoint from mobile app
    const res = await got('ACCOUNT_REGISTRATION_ENDPOINT', {
        headers: {
            // Account registration headers
            // Scrape these from mobile app, only a few are needed
        },
        form: {
            // Account registration form
            // Scrape this from mobile app
        },
        agent,
        method: 'POST'
    });

    const result = JSON.parse(res.body);
    console.log(result);
    if(result.status===1) {
        return email
    }
    throw new Error(result.status)
}

fs.readFile(PROXIES_FILE, 'utf8', async (err, data) => {
    if(err) {
        console.error(`Error reading proxies file!`.red);
        return;
    }

    const proxies = data.split(/[\r\n]+/g).filter(s => s.length !== 0 && s.includes(':'));

    let proxy = proxies[Math.floor(Math.random()*proxies.length)];

    register(proxy, CATCHALL, 'INSERT_PASSWORD_HERE');
});