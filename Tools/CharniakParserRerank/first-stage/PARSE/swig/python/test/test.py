# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.  You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations
# under the License.

import SWIGParser as parser

thread_slot = None

def dir_contents():
    print 'parser contents:', dir(parser)
    print
    print 'parser.ExtPos contents:', dir(parser.ExtPos)

def display_parses(parses):
    for i, (score, tree) in enumerate(parses):
        print i, score
        print tree
        print tree.toStringPrettyPrint()
        print

def initialize(n=10):
    # this assumes we're in PARSE/
    parser.loadModel("../DATA/EN")
    parser.setOptions('En', False, n, True, 21, 0, 0)

def test_tokenizer():
    sr = parser.tokenize("junk <s> It's some text to tokenize, if you feel like it -- or not. </s>", 399)
    print 'sr %r' % str(sr)
    print 'sr length', len(sr)
    for i in range(len(sr)):
        print 'sr word', i, sr.getWord(i).lexeme()
    return sr

def test_parse():
    sr1 = parser.SentRep(['These', 'are', 'tokens', '.'])
    sr2 = test_tokenizer()

    for sr in (sr1, sr2):
        parses = parser.parse(sr, thread_slot)
        display_parses(parses)
        print '---'

def test_as_nbest_list():
    sr1 = parser.SentRep(['These', 'are', 'tokens', '.'])
    parses = parser.parse(sr1, thread_slot)
    print parser.asNBestList(parses)

def test_extpos():
    sr1 = parser.SentRep(['record'])

    print 'Unconstrained'
    display_parses(parser.parse(sr1, thread_slot))

    print 'NN'
    ext_pos1 = parser.ExtPos()
    ext_pos1.addTagConstraints(parser.VectorString(['NN']))

    display_parses(parser.parse(sr1, ext_pos1, thread_slot))

    print 'VB'
    ext_pos2 = parser.ExtPos()
    ext_pos2.addTagConstraints(parser.VectorString(['VB']))
    display_parses(parser.parse(sr1, ext_pos2, thread_slot))

def test_multiword_extpos():
    sr1 = parser.SentRep('British left waffles on Falklands .'.split())

    print 'waffles = [anything]:'
    display_parses(parser.parse(sr1, thread_slot))

    if 1:
        print 'waffles = VBZ/VBD/VB:'
        ext_pos = parser.ExtPos()
        ext_pos.addTagConstraints(parser.VectorString([]))
        ext_pos.addTagConstraints(parser.VectorString([]))
        ext_pos.addTagConstraints(parser.VectorString(['VBZ', 'VBD', 'VB']))
        ext_pos.addTagConstraints(parser.VectorString([]))
        ext_pos.addTagConstraints(parser.VectorString([]))
        ext_pos.addTagConstraints(parser.VectorString([]))
        display_parses(parser.parse(sr1, ext_pos, thread_slot))

        print 'waffles = NNS:'
        ext_pos = parser.ExtPos()
        ext_pos.addTagConstraints(parser.VectorString([]))
        ext_pos.addTagConstraints(parser.VectorString([]))
        ext_pos.addTagConstraints(parser.VectorString(['NNS']))
        ext_pos.addTagConstraints(parser.VectorString([]))
        ext_pos.addTagConstraints(parser.VectorString([]))
        ext_pos.addTagConstraints(parser.VectorString([]))
        display_parses(parser.parse(sr1, ext_pos, thread_slot))

        print 'waffles = NN/NNS:'
        ext_pos = parser.ExtPos()
        ext_pos.addTagConstraints(parser.VectorString([]))
        ext_pos.addTagConstraints(parser.VectorString([]))
        ext_pos.addTagConstraints(parser.VectorString(['NN', 'NNS']))
        ext_pos.addTagConstraints(parser.VectorString([]))
        ext_pos.addTagConstraints(parser.VectorString([]))
        ext_pos.addTagConstraints(parser.VectorString([]))
        display_parses(parser.parse(sr1, ext_pos, thread_slot))

def test_threadslot():
    print 'parser.ThreadSlot contents:', dir(parser.ThreadSlot)
    print
    z = parser.ThreadSlot()
    print z
    print z.acquiredThreadSlot()
    print z.recycle()
    print z.acquiredThreadSlot()
    print z.acquire()
    print z.acquiredThreadSlot()

if __name__ == "__main__":
    thread_slot = parser.ThreadSlot()
    dir_contents()
    if 1:
        initialize(n=5)
        test_as_nbest_list()
        for x in range(1000): # memory leak detection
            print 'iteration', x
            test_tokenizer()
            test_parse()
            test_multiword_extpos()
            test_extpos()
