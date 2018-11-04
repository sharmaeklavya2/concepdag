"use strict";

// parse query

let params = (new URL(document.location)).searchParams;
let first_query = params.get('q');
console.log('first_query:', first_query);

if(first_query !== null && first_query !== '') {
    let searchbox = document.getElementById('searchbox');
    searchbox.value = first_query;
}

var persistence = {
    'index': null,
};

// get siteurl and rawurl

if(typeof siteurl === 'undefined') {
    var siteurl = null;
}
console.log('siteurl:', siteurl);
if(siteurl === null) {
    var siteurl = window.location.hostname;
    console.log('siteurl from window:', siteurl);
}
var raw_url = siteurl + '/searchinfo/raw.json'

// generic

function apply_to_json(url, hook) {
    console.log('apply_to_json');
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if(this.readyState == 4 && this.status == 200) {
            console.log('received request for ' + url);
            var json = JSON.parse(this.responseText);
            hook(json);
        }
    };
    xhttp.open('GET', url, true);
    xhttp.send();
}

// engine-specific

function create_elasticlunr_index(json) {
    var index = elasticlunr(function() {
        var fields = json['fields'];
        for(var i=0; i<fields.length; ++i) {
            this.addField(fields[i]);
        }
        this.setRef('uci');
    });
    console.log('index created');
    var docs = json['corpus'];
    for(var i=0; i<docs.length; ++i) {
        index.addDoc(docs[i]);
    }
    return index;
}

function search_elasticlunr_index(index, query) {
    var elasticlunr_results = index.search(query);
    console.log('elasticlunr_results:', elasticlunr_results);
    var results = []
    for(var i=0; i<elasticlunr_results.length; ++i) {
        results.push(elasticlunr_results[i]['doc']);
    }
    console.log('results:', results);
    return results;
}

if (typeof elasticlunr !== 'undefined' && elasticlunr !== null) {
    console.log('found elasticlunr');
    var create_index = create_elasticlunr_index;
    var search_index = search_elasticlunr_index;
}

// generic

function show_search_results(results) {
    var serp = document.getElementById('search-results');
    serp.innerHTML = '';
    if(results.length === 0) {
        var p = document.createElement('p');
        p.innerHTML = 'Your search did not match any documents.';
        serp.appendChild(p);
    }
    else {
        var ul = document.createElement('ul');
        var fields = [['title', true], ['uci', true], ['description', false]];
        for(var i=0; i<results.length; ++i) {
            var result = results[i];
            var li = document.createElement('li');
            var a = document.createElement('a');
            a.setAttribute('href', result['url']);
            li.appendChild(a);
            for(var j=0; j<fields.length; ++j) {
                var field = fields[j][0];
                var clickable = fields[j][1];
                if(result[field] !== undefined) {
                    var div = document.createElement('div');
                    div.classList.add('search-result-' + field);
                    div.innerHTML = result[field];
                    if(clickable) {
                        a.appendChild(div);
                    }
                    else {
                        li.appendChild(div);
                    }
                }
            }
            ul.appendChild(li);
        }
        serp.appendChild(ul);
    }
}

function ajax_hook(json) {
    var index = create_index(json);
    persistence['index'] = index;
    if(first_query !== null && first_query !== '') {
        var results = search_index(index, first_query);
    }
    else {
        var results = [];
    }
    show_search_results(results);
}

apply_to_json(raw_url, ajax_hook);
