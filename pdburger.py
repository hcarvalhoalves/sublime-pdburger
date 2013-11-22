import sublime, sublime_plugin, os

PDBRC_FILE = '~/.pdbrc'

_managers = {}

def _get_line(view, region):
    return view.rowcol(region.begin())[0] + 1


class Breakpoint(object):
    def __init__(self, manager, region):
        self.manager = manager
        self.initial_region = self.manager.view.line(region)

    def __repr__(self):
        return str(self.line)

    @property
    def key(self):
        return "bp_%d" % id(self)

    @property
    def region(self):
        r = self.manager.view.get_regions(self.key)
        return r[0] if r else self.initial_region

    @property
    def line(self):
        return _get_line(self.manager.view, self.region)

    def show(self):
        self.manager.view.add_regions(self.key, [self.initial_region],
            "markup.list", "dot", sublime.DRAW_OUTLINED)
        return self

    def hide(self):
        self.manager.view.erase_regions(self.key)
        return self

    def format_command(self):
        return 'break %s:%s' % (self.manager.view.file_name(), self.line)


class BreakpointManager(object):
    def __init__(self, view):
        self.breakpoints = []
        self.view = view

    def __repr__(self):
        return repr((self.view.file_name(), self.breakpoints))

    def __iter__(self):
        return iter(self.breakpoints)

    def indexed(self):
        return enumerate(self.breakpoints)

    def set(self, bp):
        self.breakpoints.append(bp.show())

    def unset(self, bp):
        self.breakpoints.remove(bp.hide())

    def toggle(self, region):
        bp = Breakpoint(self, region)
        for b in self.breakpoints:
            if b.region.intersects(bp.region):
               return self.unset(b)
        return self.set(bp)

    def reset(self):
        for bp in self.breakpoints:
            bp.hide()
        self.breakpoints = []


def get_manager(view):
    view_id = view.id()
    if not view_id in _managers:
        _managers[view_id] = BreakpointManager(view)
    return _managers[view_id]

def get_all_breakpoints():
    for manager in _managers.values():
        for breakpoint in manager:
            yield breakpoint

def output_pdbrc(view):
    bps = list(get_all_breakpoints())
    with open(os.path.expanduser(PDBRC_FILE), 'w') as fd:
        commands = '\n'.join([bp.format_command() for bp in bps])
        fd.write((commands + '\n').encode('utf-8'))
    if len(bps):
        message = "Added %d breakpoints to %s" % (len(bps), PDBRC_FILE)
    else:
        message = "No breakpoints"
    view.set_status('pdburger', message)


class PdburgerGotoCommand(sublime_plugin.TextCommand):
    def items(self):
        return ["Breakpoint %s: %s" % (index + 1, bp)
            for index, bp in get_manager(self.view).indexed()]

    def on_done(self, index):
        bp = dict(get_manager(self.view).indexed())[index]
        self.view.window().run_command("goto_line", {
            "line": bp.line})

    def run(self, edit):
        self.view.window().show_quick_panel(self.items(), self.on_done)


class PdburgerToggleCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        manager = get_manager(self.view)
        for region in self.view.sel():
            manager.toggle(region)
        if not self.view.is_dirty():
            output_pdbrc(self.view)


class PdburgerResetCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        manager = get_manager(self.view)
        manager.reset()
        if not self.view.is_dirty():
            output_pdbrc(self.view)


class PdburgerEventListener(sublime_plugin.EventListener):
    def on_load(self, view):
        output_pdbrc(view)

    def on_post_save(self, view):
        output_pdbrc(view)
