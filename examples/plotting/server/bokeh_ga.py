from bokeh.plotting import *
from bokeh.session import Session
from bokeh.objects import Glyph
import bokeh.embed as embed
from flask import Flask
HTML = 0
app = Flask(__name__)

@app.route("/")
def root():
	return HTML

@app.route("/fitness")
def fitness():
	renderer = [r for r in curplot().renderers if isinstance(r, Glyph)][0]
	ds = renderer.data_source
	ds.data["y"] = [4,200,2,1,0]
	ds.data["x"] = [4,400,2,1,0]
	cursession().store_objects(ds)
	return 'Done'


if __name__ == "__main__":
	global HTML
	x = [0,1,2,3,4]
	y = [0,1,2,3,4]
	output_server("line")
	plot = line(x,y, color="#0000FF", tools="pan,wheel_zoom,box_zoom,reset,previewsave")
	tag = embed.autoload_server(plot, cursession())
	html = \
	"""
	<html>
	<head></head>
	<body>
	%s

	</body>
	</html>
	"""
	HTML = html % (tag)
	app.run()