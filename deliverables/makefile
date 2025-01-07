req:
	pdflatex -output-directory=$(shell pwd)/requirementAnalysis requirementAnalysis/RequirementAnalysis.tex 
check-req:
	chktex requirementAnalysis/RequirementAnalysis.tex
plan: 
	pdflatex -output-directory=$(shell pwd)/planningDesign planningDesign/PlanningDesign.tex
check-plan:
	chktex planningDesign/PlanningDesign.tex