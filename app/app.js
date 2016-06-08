require('babel-core/register');
require('source-map-support').install();

var express = require('express'),
    cfenv = require('cfenv'),
    path = require('path'),
    bodyParser = require('body-parser'),
    fs,
    URL = require('url-parse'),
    wordSearch = require('./modules/wordSearch/index.js');

var words = JSON.parse(require('fs').readFileSync('./data/treeWords.json'));
var wordList = {"list" : words, "length" : words.length}
var tree = JSON.parse(require('fs').readFileSync('./data/pruned_tree.json'));

var app = express(),
    appEnv = cfenv.getAppEnv();

if(process.env.NODE_ENV == 'production' || process.env.NODE_ENV == 'staging'){
	app.set('port', process.env.VCAP_APP_PORT || 80);
}else{
	app.set('port', 3000);
}

app.use(express.static(path.join(__dirname, 'public')));
//app.set(path.join('views', __dirname, '/apps'));
app.use(bodyParser.urlencoded({extended: true}));
app.use(bodyParser.json());



app.get('/', function(req, res){
    res.send('index.html');
});

app.get('/randWord', function(req, res){
	res.json(wordSearch.rand(wordList));
});

app.listen(app.get('port'), function() {
    console.info('Server listening on port ' + this.address().port);
});
