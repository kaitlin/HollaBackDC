Postimage = {
	// add here the #id-s that you would like to use postimage for
	showLinkOn: Array('id_text', 'id_content'),

	// what markup do you use? see the createLink function for supported markups,
	// defaults to markdown
	markup: 'markdown',

	init: function(markup) {
		this.markup = (markup == null) ? this.markup : markup;
		if( document.getElementById('postimage') ) {
			return;
		}
		else {
			this.showLink();
		}
	},

	setMarkup: function(markup) {
		this.markup = (markup == null) ? 'markdown' : markup;
	},

	showLink: function() {
		for(id in this.showLinkOn) {
			if( document.getElementById(this.showLinkOn[id])) {
				this.showLinkFor(document.getElementById(this.showLinkOn[id]));
			}
		}
	},

	getLink: function(id) {
		var link = document.createElement('a');
		link.setAttribute('href', '/admin/postimage/attach/?for=' + id);
		link.setAttribute('target', '_blank');
		link.setAttribute('onclick', 'return showAddAnotherPopup(this);');
		var text = document.createTextNode('Attach image');
		link.appendChild(text);
		return link;
	},

	showLinkFor: function(elem) {
		elem.previousSibling.appendChild(document.createElement('br'));
		elem.previousSibling.appendChild(this.getLink(elem.id));
	},

	pathToImage: function(image) {
		var url = document.getElementById('baseurl').value;
		var root = document.getElementById('image_root').value;
		var len = root.length;
		if (root[len-1] != '/') { len += 1; };
		return url.concat(image.slice(len));
	},

	submit: function() {
		var elem = document.getElementById('id_file');
		var target = window.opener.document.getElementById(document.getElementById('for').value);
		target.value = target.value + this.createLink(document.getElementById('id_alt').value, this.pathToImage(elem.value));
		window.close();
	},

	createLink: function(alt, src) {
		switch (this.markup) {
		case 'html':
			return '\n<img alt="' + alt + '" src="' + src + '" />\n';
		case 'rst':
			return '\n.. image:: ' + src + '\n  :alt: ' + alt + '\n';
		default:
			return '\n![' + alt + '](' + src + ')\n';
			break;
		}
	}
};

addEvent(window, 'load', function() {Postimage.init();});
