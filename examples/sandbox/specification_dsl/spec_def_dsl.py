from vfworks.DSLs.specificationModel.parser.parser import *

#0. specification model
specificationModel = "input/specificationModel1.spec"

#1.setting up the parser
spec_parser = Specification_parser(specificationModel=specificationModel)
specifications = spec_parser.parse()

for spec in specifications.package.specifications:
    if spec.expression is None:
        print(spec.id+" => name: "+spec.name+" - description: "+spec.description+ " - standard: "+spec.standard+" - paragraph: "+ spec.paragraph+ "  {isMandatory="+spec.isMandatory.__str__()+"}")
    else:
        print(spec.id + " => name: " + spec.name + " - description: " + spec.description + " - standard: " + spec.standard + " - paragraph: " + spec.paragraph + " - STL: " + spec.expression.__str__() +"  {isMandatory=" + spec.isMandatory.__str__() + "}")

