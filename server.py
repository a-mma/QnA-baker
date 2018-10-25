from flask import Flask
from flask import jsonify
from flask import request

from chatbot.bot import Bot

app = Flask(__name__)

args = {
	"files": {
		"vContext": "../data/twitter_out_model.tsv",
		"dialogs": "../data/OpenSubtitles.en",
		"whoosh_index": "../whoosh_index",
		"schema_index": "schema_index",
		"context_vec_index": "context_vec_index"
	},
	"dim": 100,
	"context_limit": 10,
	"lang": u"en"
}

bot = Bot(args)

bot_context = []

@app.route("/load", methods=['POST'])
def load():
	bot.preloadDB()
	return jsonify({"status":200})

@app.route("/talk", methods=['POST'])
def talk():
	global bot_context
	question = request.json['q']
	result = bot.answer(question.lower())
	bot_context.append(question)
	bot_context.append(result)
	return jsonify({"a":result, "context":bot_context})

@app.route("/reset", methods=['POST'])
def reset():
	global bot_context
	bot_context = []
	return jsonify({"status":200})

if __name__ == '__main__':
	app.run('0.0.0.0', 5000)