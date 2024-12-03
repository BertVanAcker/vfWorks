Package {
    PackageID: PKG_001
    PackageName: "Sample Package"
    Specifications: {
        Specification {
                 ID: SPEC_001
                 Name: "SPECIFICATION1"
                 Description: "THIS IS A DUMMY SPECIFICATION"
                 Standard: "ISO26262-part3"
                 Paragraph: "3.1.2 - processes"
                 DOI: "10.1234/example.doi"
                 IsMandatory: True
         },
         Specification {
             ID: SPEC_002
             Name: "SPECIFICATION2"
             Description: "THIS IS A DUMMY SPECIFICATION"
             Standard: "ISO26262-part2"
             Paragraph: "2.5 - V&V"
             DOI: "10.5678/another.doi"
             STL: G (drift<0.1)
             IsMandatory: True
         },
         Specification {
             ID: SPEC_002
             Name: "SPECIFICATION3"
             Description: "THIS IS A DUMMY SPECIFICATION"
             Standard: "ISO26262-part2"
             Paragraph: "2.5 - V&V"
             DOI: "10.5678/another.doi"
             STL: (motorThrust > 0) & (motorThrust < 10000)
             IsMandatory: True
         }
     }
}

