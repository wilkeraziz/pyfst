from libcpp.vector cimport vector
from libcpp.string cimport string
from libcpp.pair cimport pair
from libc.stdint cimport uint64_t
from util cimport ostream, istream

cimport sym

cdef extern from "<fst/fstlib.h>" namespace "fst":
    enum:
        kIDeterministic
        kODeterministic
        kAcceptor
        kTopSorted
        kWeighted

    cdef cppclass Weight:
        pass

    cdef cppclass Arc[W]:
        int ilabel
        int olabel
        int nextstate
        Arc(int ilabel, int olabel, W& weight, int nextstate)
        W weight

    cdef cppclass ArcIterator[T]:
        ArcIterator(T& fst, int state)
        bint Done()
        void Next()
        Arc& Value()

    cdef cppclass Fst:
        int Start()
        unsigned NumArcs(int s)
        Fst* Copy()
        bint Write(string& filename)
        uint64_t Properties(uint64_t mask, bint compute)

    cdef cppclass ExpandedFst(Fst):
        int NumStates()

    cdef cppclass MutableFst(ExpandedFst):
        int AddState()
        void SetFinal(int s, Weight w)
        void SetStart(int s)
        void SetInputSymbols(sym.SymbolTable* isyms)
        void SetOutputSymbols(sym.SymbolTable* osyms)
        sym.SymbolTable* MutableInputSymbols()
        sym.SymbolTable* MutableOutputSymbols()

    cdef cppclass FstHeader:
        void Read(istream& stream, string& source)
        string ArcType()
        string FstType()

{{#types}}
    cdef cppclass {{weight}}(Weight):
        float Value()
        {{weight}}(float value)
        {{weight}}({{weight}} weight)
        bint operator==({{weight}}& other)
        {{weight}}& set_value "operator=" ({{weight}}& other)

    cdef {{weight}} Plus({{weight}} &w1, {{weight}}& w2)
    cdef {{weight}} Times({{weight}} &w1, {{weight}}& w2)

    cdef {{weight}} {{weight}}Zero "fst::{{weight}}::Zero" ()
    cdef {{weight}} {{weight}}One "fst::{{weight}}::One" ()

    ctypedef Arc[{{weight}}] {{arc}}

{{/types}}

    cdef cppclass StdVectorFst(MutableFst):
        TropicalWeight Final(int s)
        void AddArc(int s, StdArc &arc)

    cdef cppclass LogVectorFst "fst::VectorFst<fst::LogArc>" (MutableFst):
        LogWeight Final(int s)
        void AddArc(int s, LogArc &arc)

    cdef StdVectorFst* StdVectorFstRead "fst::StdVectorFst::Read" (string& filename)
    cdef LogVectorFst* LogVectorFstRead "fst::VectorFst<fst::LogArc>::Read" (string& filename)

    cdef cppclass ILabelCompare[A]:
        pass

    cdef cppclass OLabelCompare[A]:
        pass

    cdef cppclass ArcMapper:
        pass

{{#types}}
    cdef cppclass Plus{{arc}}Mapper "fst::PlusMapper<fst::{{arc}}>"(ArcMapper):
        Plus{{arc}}Mapper({{weight}})
    cdef cppclass Times{{arc}}Mapper "fst::TimesMapper<fst::{{arc}}>"(ArcMapper):
        Times{{arc}}Mapper({{weight}})
    cdef cppclass Rm{{weight}}Mapper "fst::RmWeightMapper<fst::{{arc}}>"(ArcMapper):
        Rm{{weight}}Mapper()
    cdef cppclass {{convert}}WeightConvertMapper "fst::WeightConvertMapper<fst::{{other}}Arc, fst::{{arc}}>"(ArcMapper):
        {{convert}}WeightConvertMapper()
{{/types}}
        

    enum ProjectType:
        PROJECT_INPUT
        PROJECT_OUTPUT

    enum ClosureType:
        CLOSURE_STAR
        CLOSURE_PLUS

    cdef bint Equivalent(Fst& fst1, Fst& fst2)

    # const
    cdef void Compose(Fst &ifst1, Fst &ifst2, MutableFst* ofst)
    cdef void Determinize(Fst& ifst, MutableFst* ofst)
    cdef void Difference(Fst &ifst1, Fst &ifst2, MutableFst* ofst)
    cdef void Intersect(Fst &ifst1, Fst &ifst2, MutableFst* ofst)
    cdef void Reverse(Fst &ifst, MutableFst* ofst)
    cdef void ShortestPath(Fst &ifst, MutableFst* ofst, unsigned n)
    cdef void ArcMap (Fst &ifst, MutableFst* ofst, ArcMapper mapper)
{{#types}}
    cdef void ShortestDistance(Fst &fst, vector[{{weight}}]* distance, bint reverse)
{{/types}}
    # non const
    cdef void Closure(MutableFst* ifst, ClosureType type)
    cdef void Invert(MutableFst* ifst)
    cdef void Minimize(MutableFst* fst)
    cdef void Project(MutableFst* fst, ProjectType type)
    cdef void Relabel(MutableFst* fst, 
            vector[pair[int, int]]& ipairs,
            vector[pair[int, int]]& opairs)
    cdef void RmEpsilon(MutableFst* fst)
    cdef void TopSort(MutableFst* fst)
{{#types}}
    cdef void ArcSort(MutableFst* fst, ILabelCompare[{{arc}}]& compare)
    cdef void ArcSort(MutableFst* fst, OLabelCompare[{{arc}}]& compare)
    cdef void Prune(MutableFst* ifst, {{weight}} threshold)
{{/types}}
    # other
    cdef void Union(MutableFst* ifst1, Fst &ifst2)
    cdef void Concat(MutableFst* ifst1, Fst &ifst2)

cdef extern from "<fst/script/draw.h>" namespace "fst":
    cdef cppclass FstDrawer[A]:
        FstDrawer(Fst& fst, 
                  sym.SymbolTable *isyms,
                  sym.SymbolTable *osyms,
                  sym.SymbolTable *ssyms,
                  bint accep,
                  string title,
                  float width,
                  float height,
                  bint portrait,
                  bint vertical, 
                  float ranksep,
                  float nodesep,
                  int fontsize,
                  int precision,
                  bint show_weight_one)

        void Draw(ostream *strm, string &dest)
