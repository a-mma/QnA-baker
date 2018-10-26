# QnA baker
Create your own context aware QnA bot with this tool as a microservice. It provides a simple API to load your data and make predictions. 

### How it works?
* Thanks to ***Starspace*** from Facebook research. Which works as backbone for this project (details below).
* Thanks to ***Whoosh***. Which helped to move GBs of data from Main Memory to disk.

![screenshot from 2018-10-25 22-10-58](https://user-images.githubusercontent.com/19545678/47516389-fe723800-d8a2-11e8-9a41-5f7e98dead35.png)
> more details on how this work is given below.

### Requirements:
```
Starspace
---------
follow this link: https://github.com/facebookresearch/Starspace

Python 3
--------
Python modules:
1. Numpy: pip3 install numpy
2. Whoosh: pip3 install Whoosh
3. Sklearn: pip3 install scikit-learn
4. flask: pip3 install flask
```

### How to use?
* First of all you need to generate word embeddings from Starspace
    * Download a context oriented dialog dataset. You can try these, for example: [link1](https://github.com/Phylliida/Dialogue-Datasets/blob/master/TwitterLowerAsciiCorpus.txt) [link2](http://opus.nlpl.eu/download.php?f=OpenSubtitles/en-es.txt.zip) [link3](http://opus.nlpl.eu/)
    * From the above dataset, generate Starspace friendly input file for training. You can refer [this](https://github.com/facebookresearch/StarSpace#docspace-document-recommendation) section on Starspace documentation. Each line in the document shold represent a single dialog context. Where each dialog turn (dialog sentance) is seperated with a `<tab>` character. For example, `<context 1 dialog sentance 1><tab><context 1 dialog sentance 2><tab><context 1 dialog sentance 3><tab>...`. Note that, each dialog sentance is a string having words seperated with a `<whitespace>` character. Like, `..tab><context 1 dialog sentance 2 word 1><whitespace><context 1 dialog sentance 2 word 2><whitespace><context 1 dialog sentance 2 word 3><tab..`.
    * Once the training file is generated, train with  `starspace train -trainFile <input file> -model <model name> -trainMode 1 -fileFormat labelDoc` and generate word embeddings. Currently, QnA baker don't support n-gram embedding.
    * Once training is done, we need a copy of the generated `<model name>.tsv` file.
* Step 2 is to index embeddings and dialogs
    * Clone this repository to your local machine. Create a `data` directory and keep a copy of `<model name>.tsv` there.
    * Create another file `<conversation data>.txt`, which is a modified copy of actual dialog dataset that we need to index. In this document, each line represent a single dialog turn in our dataset and are arranged in the order of actual conversation within a context. Each group of dialogs (each context) is seperated by a blank line. For example, `...<\n><context 1 dialog sentance 1><\n><context 1 dialog sentance 2><\n><context 1 dialog sentance 3><\n><\n><context 2 dialog sentance 1><\n><context 2 dialog sentance 2><\n><context 2 dialog sentance 3><context 2 dialog sentance 4><\n><context 2 dialog sentance 5><\n><\n>...`
    * Modify, `server.py` by specifying the file locations for `vContext` (path to <model name>.tsv) and `dialogs` (path to <conversation data>.txt). And any other value, if you like.
    * Now, run the project with `python3 server.py`. And Use a REST client to access `http://0.0.0.0:5000/`.
* API interfaces
    * [POST] /load -  Load and index word embeddings and conversation text. This should be done at first and once. It will take some time (minutes to hours) based on the data you are feeding.
    * [POST] /talk - Once data is loaded, start talking to the bot. *Request header: `Content-Type: application/json` body: `{"q": "<query to bot>"}`*.
    * [POST] /reset - Reset user-bot dialog context and start new conversation.

### Things to consider:
* Currently, the data is assumed to be cleaned already.
* If you are using python2, note that, Whoosh requires the data be in Unicode format.

### To do:
* User management in API
* Enable ngram embedding to support more languages
* Automate & integrate Starspace training (Once a python wrapper is available)
* Dockerize
* Return confidence score with /talk API (to make this compatible with other bot frameworks)
* Integrate basic data cleaning
* Make it fast - can [FAISS](https://github.com/facebookresearch/faiss) help us?

### Experimental ideas that we can try out on this:
* Weighted sort candidate answers based on user's current sentiment
* Multiple languages within a single context (flexibility to talk in multiple languages) - can [MUSE](https://github.com/facebookresearch/MUSE) help us?
* User/situation aware answer rephrasing within context given a set of slots.

### Test:
Here is a quick test did with the bot (used link2 in the above datasets - raw data). => is bot.

> hey babe

>   => I don' t need no arms around me

> you don't have arms. I know that.

>   => You don' t have to go, do you?

> where

>   => - London?

> no I am not going to london

>   => - Yes, London.

> no I am not going to london

>   => Not for me.

> not for anyone in this earth

>   => Here you go, two Imhoteps.

> ok. I don't understand.

>   => - \"What' s that, Dad?\"

> dad? I am not your dad.

>   => Oh, I' m sorry.

> good for you

>   => You' ve been fired?

> no

>   => It' s your party, your ****, his **** **** **** ****.

> what the ****

>   => That was a shitty thing to do!

> yes I know that already

>   => I' m tired of brain- storming.

> cool

>   => L...... of our most sacred company policies to ensure that you have all the skills necessary

> ok

>   => OK, OK.

> ok

>   => Oh my God,

> what happened

>   => - Why didn' t you try to be a cowboy?

> I hate cowboys

>   => I hate 'em.

> wow that's cool

>   => Leave it.

> ok

>   => Oh my God,

> what happened again?

>   => That' s not fair.

> what happened? tell me..

>   => Don' t tell her!

> no, I wouldn't tell

>   => Look, if everybody can be down there, why can' t I?

> sorry, i can't get you.

>   => I' il take a beer.

> you are drunk already

>   => Drunken sword?

> no. drunken freak

>   => Freeze!

> what now?

>   => I have an idea.

> tell me

>   => Okay, just cool it.

> cool what

>   => Splash some water on your face.

> why should I

>   => A just question, my liege.

> hmm

>   => What?

> hmm

>   => What?

> hmm

>   => What?

> hmm

>   => Can we work this out or not?

> I can't do that. I'm confused

>   => The Kensington and Dillworth jewel thief has struck again.

> Again? Oh My God

>   => Hello, Miss Phillips.

> what? who?

>   => - The fairest goddess.

> oh! I see..

>   => When you say it' s over, you mean it' s over.

> ok. Its over

>   => - OK.

> its over again

>   => My names Elizabeth Swann.
	
### How it works internally? What is the motivation?
*To be done.*

### Contribute:
Please see `To do` and `ideas` section above. If anyone can help with a Starspace python wrapper, it will be great. And will make things a lot easier.

## reference:
> @article{wu2017starspace,
  title={StarSpace: Embed All The Things!},
  author = {{Wu}, L. and {Fisch}, A. and {Chopra}, S. and {Adams}, K. and {Bordes}, A. and {Weston}, J.},
  journal={arXiv preprint arXiv:{1709.03856}},
  year={2017}
}
