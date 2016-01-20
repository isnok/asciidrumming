import pprint

def parse_composition_raw(name):

    global section_parsers
    raw_composition = {section: [] for section in section_parsers}
    with open(name, 'r') as fh:
        block = 'initial'
        for line in fh.readlines():
            line = line.split('#')[0].strip()
            if not line:
                continue

            if line.startswith('['):
                assert line.endswith(']')
                block = line[1:-1]
            else:
                raw_composition[block].append(line)

    composition = {
        section: parser(raw_composition[section])
        for section, parser in section_parsers.items()
    }

    return composition

def parse_dict_simple(lines):
    parsed = {}
    for line in lines:
        if line.count(':') == 1:
            key, value = line.split(':')
            parsed[key.strip()] = value.strip()
        elif line.count(':') == 2:
            key, _, value = line.split(':')
            parsed[key.strip()+':'] = value.strip()
        else:
            print('parse_dict_simple ignored line:', repr(line))
    return parsed

def parse_initial(lines):
    return parse_dict_simple(lines)

def parse_voices(lines):
    raw = parse_dict_simple(lines)
    voices = {}
    for k, value in raw.items():
        voice, char = k.split('_')
        if voice in voices:
            voices[voice][char] = value
        else:
            voices[voice] = {char: value}
    return voices

def parse_verses(lines):

    def chunker(lines):
        chunk = []
        for line in lines:
            if line == '--':
                yield chunk
                chunk = []
            else:
                chunk.append(line)
        yield chunk

    #def parse_chunk(chunk):
        #parsed = parse_dict_simple(chunk)
        #return parsed

    parsed = [parse_dict_simple(chunk) for chunk in chunker(lines) if chunk]

    return parsed

def parse_phrases(lines):

    def chunker(lines):
        chunk = []
        for line in lines:
            if ':' in line:
                yield chunk
                chunk = [line]
            else:
                chunk.append(line)
        yield chunk

    def header_args(strings):
        args = {}
        for s in strings:
            k, v = s.split('=')
            args[k.strip()] = v.strip()
        return args

    def parse(chunk):
        header = chunk[0].split(':')
        name = header[0].strip()
        args = header_args(header[1].split())
        phrase = ''
        for line in chunk[1:]:
            phrase += line.replace(' ', '')
        parsed = {
            'name': name,
            'pattern': phrase,
        }
        parsed.update(args)
        return parsed

    raw = [parse(chunk) for chunk in chunker(lines) if chunk]

    parsed = {}
    for section in raw:
        parsed[section.pop('name')] = section

    return parsed

section_parsers = {
    'initial':parse_initial,
    'verses':parse_verses,
    'voices':parse_voices,
    'phrases':parse_phrases,
}

def parse_composition(name):

    raw = parse_composition_raw(name)

    def convert(value):
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError as ex:
            return value

    def convert_values(collection):
        if isinstance(collection, list):
            return [convert_values(x) for x in collection]
        elif isinstance(collection, dict):
            converted = {}
            for k, v in collection.items():
                if isinstance(v, (list, dict)):
                    converted[k] = convert_values(v)
                else:
                    converted[k] = convert(v)
            return converted
        else:
            return convert(collection)

    return convert_values(raw)


def main(composition):
    raw = parse_composition(composition)
    pprint.pprint(raw)

if __name__ == '__main__':
    import sys
    main(sys.argv[1])
