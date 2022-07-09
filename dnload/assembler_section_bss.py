from dnload.assembler_section import AssemblerSection
from dnload.platform_var import PlatformVar

########################################
# AssemblerSectionBss ##################
########################################

class AssemblerSectionBss(AssemblerSection):
    """.bss section to be appended to the end of assembler source files."""

    def __init__(self, imports=None):
        """Constructor."""
        AssemblerSection.__init__(self, "bss")
        self.__elements = []
        self.__imports = imports
        self.__size = 0
        self.__und_size = 0

    def add_element(self, op):
        """Add one variable element."""
        if op in self.__elements:
            print("WARNING: trying to add .%s element twice: %s" % (sekf.__name, str(element)))
            return
        self.__elements += [op]
        self.__elements.sort()
        self.__size += op.get_size()
        if op.is_und_symbol():
            self.__und_size += op.get_size()

    def create_content(self, assembler, prepend_label=None):
        """Generate assembler content."""
        self.clear_content()
        addr_size = int(PlatformVar("addr"))
        if prepend_label:
            self.add_content(assembler.format_label(prepend_label))
        if 0 < self.__size:
            self.add_content(assembler.format_align(addr_size))
            self.add_content(assembler.format_label("aligned_end"))
        if 0 < self.get_alignment():
            self.add_content(assembler.format_align(self.get_alignment()))

        if self.__imports:
            self.add_content(assembler.format_equ('GOTPCREL', "aligned_end" if 0 < self.__size else 'end'))
            ix = 0
            for imp in self.__imports:
                # self.add_content(assembler.format_equ(f'got_{imp}', "GOTPCREL + %i" % (ix)))
                self.add_content(assembler.format_equ(imp, "GOTPCREL + %i" % (ix)))
                ix += addr_size

            self.add_content(assembler.format_equ("got_end", "GOTPCREL + %i" % (ix)))
            self.add_content(assembler.format_equ('bss_start', 'got_end'))
        else:
            self.add_content(assembler.format_label("bss_start"))
        cumulative = 0
        for ii in self.__elements:
            self.add_content(assembler.format_equ(ii.get_name(), "bss_start + %i" % (cumulative)))
            cumulative += ii.get_size()
        self.add_content(assembler.format_equ("bss_end", "bss_start + %i" % (cumulative)))

    def get_alignment(self):
        """Get alignment. May be zero."""
        # TODO: Probably creates incorrect binaries at values very close but less than 128M due to code size.
        if 128 * 1024 * 1024 < self.get_size():
            return int(PlatformVar("memory_page"))
        return 0

    def get_size(self):
        """Get total size."""
        return self.__size
