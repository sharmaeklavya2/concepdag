# ConcepDAG

ConcepDAG is a tool to visualize dependencies between concepts.
For each concept, create a JSON file which describes the concept itself
and which lists out the concepts it depends on.
ConcepDAG will take all these JSON files as input and create a static website
([example](https://sharmaeklavya2.github.io/theoremdep/)).

ConcepDAG is inspired by [Metacademy](https://metacademy.org/about).

## How to use it?

To use ConcepDAG, you must run `python3 main.py` with the right command-line arguments.
You must specify 3 directories in the command-line:

* `input_dir`: Directory where you'll put all content.
* `intermediate_dir`: Directory to store intermediate output.
* `output_dir`: Directory where the static site will be generated.

`input_dir` can (but need not) contain the following files/directories:

* `nodes`: Directory which should contain all your JSON files.
* `includes`: Directory which contains Markdown/HTML/plain-text files.
  If you want to describe a concept in detail, you can either write about it in JSON files in `nodes`
  or you can do write about it in files in `includes` and refer them from the JSON files.
* `config.json`: File for configuring the static website.
  Here you can specify metadata about the website and add additional stylesheets and scripts.

All sub-directories are optional; but of course, you won't get any output if there's no input!

You can also specify a theme to use to generate the website.
If you don't do that, the default theme will be used.

### Example

I used ConcepDAG to create [TheoremDep](https://sharmaeklavya2.github.io/theoremdep/),
a website to track dependencies between theorems.

You can view the `input_dir` for TheoremDep at its source repository:
<https://github.com/sharmaeklavya2/theoremdep-source>

### `nodes` JSON schema

Coming soon.

### `config.json` schema

Coming soon.

## How is ConcepDAG different from Metacademy?

Metacademy tracks prerequisites between 'concepts to learn' (to learn A, you must learn B).
ConcepDAG is made with a more general prerequisite-tracking aim in mind.

The main difference is that ConcepDAG generates a static website,
whereas Metacademy is a dynamic web application.

* Metacademy is slow.
  I'm disappointed by the speed of their servers.
  A static website can be faster.
* Deploying an instance of a dynamic website is either difficult or costly.
* Metacademy allows easy content updation. ConcepDAG can't do that (yet).

## Freedom to use

&copy; 2021 Eklavya Sharma

All code is licensed under the [MIT license](https://choosealicense.com/licenses/mit/).
This roughly means that you are free to use, modify and distribute this code.
