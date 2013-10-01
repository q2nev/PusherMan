# XML Parser/Data Access Object game.py
"""AUTO-GENERATED Source file for game.py"""
import xml.sax
import Queue
import Q2API.xml.base_xml

rewrite_name_list = ("name", "value", "attrs", "flatten_self", "flatten_self_safe_sql_attrs", "flatten_self_to_utf8", "children")

def process_attrs(attrs):
    """Process sax attribute data into local class namespaces"""
    if attrs.getLength() == 0:
        return {}
    tmp_dict = {}
    for name in attrs.getNames():
        tmp_dict[name] = attrs.getValue(name)
    return tmp_dict

def clean_node_name(node_name):
    clean_name = node_name.replace(":", "_").replace("-", "_").replace(".", "_")

    if clean_name in rewrite_name_list:
        clean_name = "_" + clean_name + "_"

    return clean_name

class desc_q2class(Q2API.xml.base_xml.XMLNode):
    def __init__(self, attrs):
        self.level = 4
        self.path = [None, u'game', u'player', u'item']
        Q2API.xml.base_xml.XMLNode.__init__(self, "desc", attrs, None, [])

class usage_q2class(Q2API.xml.base_xml.XMLNode):
    def __init__(self, attrs):
        self.level = 4
        self.path = [None, u'game', u'player', u'item']
        Q2API.xml.base_xml.XMLNode.__init__(self, "usage", attrs, None, [])

class item_q2class(Q2API.xml.base_xml.XMLNode):
    def __init__(self, attrs):
        self.level = 3
        self.path = [None, u'game', u'player']
        self.usage = []
        self.desc = []
        Q2API.xml.base_xml.XMLNode.__init__(self, "item", attrs, None, [])

class place_q2class(Q2API.xml.base_xml.XMLNode):
    def __init__(self, attrs):
        self.level = 3
        self.path = [None, u'game', u'stop']
        self.desc = []
        Q2API.xml.base_xml.XMLNode.__init__(self, "place", attrs, None, [])

class player_q2class(Q2API.xml.base_xml.XMLNode):
    def __init__(self, attrs):
        self.level = 2
        self.path = [None, u'game']
        self.item = []
        Q2API.xml.base_xml.XMLNode.__init__(self, "player", attrs, None, [])

class scenario_q2class(Q2API.xml.base_xml.XMLNode):
    def __init__(self, attrs):
        self.level = 2
        self.path = [None, u'game']
        Q2API.xml.base_xml.XMLNode.__init__(self, "scenario", attrs, None, [])

class stop_q2class(Q2API.xml.base_xml.XMLNode):
    def __init__(self, attrs):
        self.level = 2
        self.path = [None, u'game']
        self.item = []
        self.place = []
        self.desc = []
        Q2API.xml.base_xml.XMLNode.__init__(self, "stop", attrs, None, [])

class game_q2class(Q2API.xml.base_xml.XMLNode):
    def __init__(self, attrs):
        self.level = 1
        self.path = [None]
        self.scenario = []
        self.stop = []
        self.player = []
        Q2API.xml.base_xml.XMLNode.__init__(self, "game", attrs, None, [])

class NodeHandler(xml.sax.handler.ContentHandler):
    """SAX ContentHandler to map XML input class/object"""
    def __init__(self, return_q):     # overridden in subclass
        self.obj_depth = [None]
        self.return_q = return_q
        self.last_processed = None
        self.char_buffer = []
        xml.sax.handler.ContentHandler.__init__(self)   # superclass init

    def startElement(self, name, attrs): # creating the node along the path being tracked
        """Override base class ContentHandler method"""
        name = clean_node_name(name)
        p_attrs = process_attrs(attrs)

        if name == "":
            raise ValueError, "XML Node name cannot be empty"

        elif name == "scenario":
            self.obj_depth.append(scenario_q2class(p_attrs))

        elif name == "item":
            self.obj_depth.append(item_q2class(p_attrs))

        elif name == "stop":
            self.obj_depth.append(stop_q2class(p_attrs))

        elif name == "player":
            self.obj_depth.append(player_q2class(p_attrs))

        elif name == "game":
            self.obj_depth.append(game_q2class(p_attrs))

        elif name == "place":
            self.obj_depth.append(place_q2class(p_attrs))

        elif name == "usage":
            self.obj_depth.append(usage_q2class(p_attrs))

        elif name == "desc":
            self.obj_depth.append(desc_q2class(p_attrs))

        self.char_buffer = []
        self.last_processed = "start"

    def endElement(self, name): # need to append the node that is closing in the right place
        """Override base class ContentHandler method"""
        name = clean_node_name(name)

        if (len(self.char_buffer) != 0) and (self.last_processed == "start"):
            self.obj_depth[-1].value = "".join(self.char_buffer)

        if name == "":
            raise ValueError, "XML Node name cannot be empty"

        elif name == "scenario":
            self.obj_depth[-2].scenario.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        elif name == "item":
            self.obj_depth[-2].item.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        elif name == "stop":
            self.obj_depth[-2].stop.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        elif name == "player":
            self.obj_depth[-2].player.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        elif name == "game":
            # root node is not added to a parent; stays on the "stack" for the return_object
            self.char_buffer = []
            self.last_processed = "end"
            return

        elif name == "place":
            self.obj_depth[-2].place.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        elif name == "usage":
            self.obj_depth[-2].usage.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        elif name == "desc":
            self.obj_depth[-2].desc.append(self.obj_depth[-1]) #  make this object a child of the next object up...
            self.obj_depth[-2].children.append(self.obj_depth[-1]) #  put a reference in the children list as well
            self.obj_depth.pop() # remove this node from the list, processing is complete
            self.char_buffer = []

        self.last_processed = "end"


    def characters(self, in_chars):
        """Override base class ContentHandler method"""
        self.char_buffer.append(in_chars)

    def endDocument(self):
        """Override base class ContentHandler method"""
        self.return_q.put(self.obj_depth[-1])

def obj_wrapper(xml_stream):
    """Call the handler against the XML, then get the returned object and pass it back up"""
    try:
        return_q = Queue.Queue()
        xml.sax.parseString(xml_stream, NodeHandler(return_q))
        return (True, return_q.get())
    except Exception, e:
        return (False, (Exception, e))


