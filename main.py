from View import view
from Model import modelcsv
from Controller import controller, mvc_exc

c = controller.Controller(modelcsv.ModelCsv(), view.ViewTkinter())