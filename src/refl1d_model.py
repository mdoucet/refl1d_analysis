"""
"""
import logging
import json, re

def parse_single_param(line):
    """
        Parse a line of the refl1d DREAM output log
        1            intensity  1.084(31)  1.0991  1.1000 [  1.062   1.100] [  1.000   1.100]
        2              air rho 0.91(91)e-3 0.00062 0.00006 [ 0.0001  0.0017] [ 0.0000  0.0031]

    """
    result = re.search(r'^\d+ (.*) ([\d.-]+)\((\d+)\)(e?[\d-]*)\s* [\d.-]+\s* ([\d.-]+)(e?[\d-]*) ', line.strip())
    value_float = None
    error_float = None
    par_name = None
    if result is not None:
        par_name = result.group(1).strip()
        exponent = result.group(4)
        mean_value = "%s%s" % (result.group(2), exponent)
        error = "%s%s" % (result.group(3), exponent)
        best_value = "%s%s" % (result.group(5), result.group(6))

        # Error string does not have a .
        err_digits = len(error)
        val_digits = len(mean_value.replace('.',''))
        err_value = ''
        i_digit = 0

        for c in mean_value: #pylint: disable=invalid-name
            if c == '.':
                err_value += '.'
            else:
                if i_digit < val_digits - err_digits:
                    err_value += '0'
                else:
                    err_value += error[i_digit - val_digits + err_digits]
                i_digit += 1

        error_float = float(err_value)
        value_float = float(best_value)
    return par_name, value_float, error_float


class ReflectivityModel(object):
    def __init__(self, info, layers):
        self.refl_model = info
        self.layers = layers
        
        if 'data_path' in info:
            self.name = info['data_path']
        else:
            self.name = ''

        if 'chi2' in info:
            self.chi2 = info['chi2']
        else:
            self.chi2 = 0

    def __repr__(self):
        """ Pretty print this model """
        printout = "----- Model: %s    [chi2=%s]\n" % (self.name, self.chi2)

        for key in self.refl_model.keys():
            if key not in ['chi2', 'data_path', 'info']:
                printout += "   %15s\t %s\n" % (key, self.refl_model[key])
        printout += '\n'

        for layer_name, l in self.layers.items():
            layer_str = 'Layer %s:  \n    ' % layer_name
            mag_str = '    '
            k_list = {}
            

            
            for p in sorted(l.keys()):
                k_list[p.replace(layer_name, '').strip()] = l[p] 
            
            for p in sorted(k_list.keys(), key=str.lower):
                if p == 'info':
                    continue

                if p.endswith('M') or 'interfaceM' in p or 'deadM' in p:
                    mag_str += '%s=%s, ' % (p.replace(layer_name, '').strip(), k_list[p])
                else:
                    layer_str += '%s=%s, ' % (p.replace(layer_name, '').strip(), k_list[p])

            printout += "%s\n" % layer_str
            printout += "%s\n\n" % mag_str
        
        printout += '\n'
        return printout
            

class ReflectivityProblem(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.model_list = []
        self.fit_params = []

        with open('%s.err' % file_path, 'r') as fd:
            self.model_list, chi2, self.fit_params = self.parse_slabs(fd.read())

    def parse_slabs(self, content):
        """
            Parse the content of a refl1d log file.
            The part we are parsing is the list of models that looks like
            a dump of python objects written in a weird format:

            .sample
              .layers
                [0]
                  .interface = Parameter(1.46935, name='Si interface', bounds=(1,5))
                  .material
                    .irho = Parameter(0, name='Si irho')
                    .rho = Parameter(2.07, name='Si rho')
                  .thickness = Parameter(0, name='Si thickness')
        """
        refl_model = dict(data_path="none")
        current_layer = {}
        current_layer_name = None
        layers = {}
        chi2 = 0

        in_probe = False
        in_sample = False
        model_names = []
        discovered_names = []
        model_list = []
        output_params = []

        for l in content.split('\n'):
            if l.startswith("[chisq="):
                in_sample = False
                result = re.search(r'chisq=([\d.]*)', l)
                if result is not None:
                    refl_model['chi2'] = result.group(1)
                # Chi2 is the last thing we get for a model, so
                # clean thing up here.
                if len(current_layer) > 0:
                    layers[current_layer_name] = current_layer
                    model_list.append([refl_model, layers])
                    
            if l.startswith("[overall chisq="):
                result = re.search(r'chisq=([\d.]*)', l)
                if result is not None:
                    chi2 = result.group(1)
            if l.startswith("SIMULTANEOUS"):
                clean_str = l.replace("SIMULTANEOUS ", "")
                model_names = json.loads(clean_str)

            if l.startswith("-- Model"):
                result = re.search(r"-- Model (\d+)", l)
                if result is not None:
                    layers = {}
                    current_layer = {}
                    current_layer_name = None
                    if len(model_names) <= int(result.group(1)):
                        model_names.append(result.group(1))
                    refl_model = dict(data_path=model_names[int(result.group(1))])

            # PROBE section
            #TODO: read in the mm, mp, pm, pp info separately
            if l.startswith('.probe'):
                in_probe = True
            elif in_probe:
                result = re.search(r".(\w*) = Parameter\((.*), name='(\w*)'", l)
                if result is not None:
                    if result.group(1) == 'background':
                        refl_model['background'] = result.group(2)
                    elif result.group(1) == 'intensity':
                        refl_model['intensity'] = result.group(2)
                    elif result.group(1) == 'Aguide':
                        refl_model['Aguide'] = result.group(2)
                    elif result.group(1) == 'H':
                        refl_model['H'] = result.group(2)

            # SAMPLE section
            if l.startswith('.sample'):
                in_probe = False
                in_sample = True
            elif in_sample:
                result = re.search(r"\[(\d+)\]", l)
                if result is not None:
                    if len(current_layer) > 0:
                        layers[current_layer_name] = current_layer
                    current_layer = {}
                    current_layer_name = None

                for name in [r"\.interface", r"\.irho", r"\.rho", r"\.thickness",
                             r"\.dead_above", r"\.dead_below",
                             r"\.interface_above", r"\.interface_below",
                             r"\.rhoM", r"\.thetaM"]:
                    result = re.search(r"%s = Parameter\((.*), name='([\w ]*)'" % name, l)
                    if result is not None:
                        current_layer[result.group(2)] = result.group(1)
                        if current_layer_name is None:
                            toks = result.group(2).split(' ')
                            current_layer_name = toks[0].strip() 

            par_name, value, error = parse_single_param(l)
            if par_name is not None:
                # Look for a model name
                # Parameter names are [model name] [layer name] [parameter name]
                # First get rid of misleading tokens
                _par_name = par_name.replace('above', '')
                _par_name = par_name.replace('below', '')
                _name_toks = _par_name.strip().split(' ')
                name_toks = par_name.strip().split(' ')
                
                if len(_name_toks) >= 3:
                    #par_name = ' '.join(name_toks[1:])
                    if name_toks[0] not in discovered_names:
                        model_id = len(discovered_names)
                        model_list[model_id][0]['data_path'] = name_toks[0]
                        discovered_names.append(name_toks[0])

                output_params.append([par_name, value, error])

        # Sort out the models
        clean_model_list = {}
        for r_model, l_model in model_list:
            clean_model_list[r_model['data_path']] = (ReflectivityModel(r_model, l_model))
        return clean_model_list, chi2, output_params

    def replace(self, parameter_list):
        """ Replace fit parameters in our models """
        if not len(self.fit_params) == len(parameter_list):
            logging.error("Parameter list of wrong length: found %s and expected %s" % (len(self.fit_params), len(parameter_list)))
        
        for i in range(len(self.fit_params)):
            # Skip background and intensity for now since they have the same names for both models
            if self.fit_params[i][0] in ['background', 'intensity']:
                continue
            toks = self.fit_params[i][0].split(' ')
            par_name = self.fit_params[i][0]
            if toks[0] in self.model_list.keys():
                layer_name = toks[1]
                par_name = par_name.replace(toks[0], '').strip()
                self.model_list[toks[0]].layers[layer_name][par_name] = parameter_list[i]
            else:
                layer_name = toks[0]
                for m in self.model_list.keys():
                    self.model_list[m].layers[layer_name][par_name] = parameter_list[i]
            
    def __repr__(self):
        """ Pretty print the fit problem """
        printout = ""
        for m in self.model_list:
            printout += str(self.model_list[m])
        i_count = 0
        for item in self.fit_params:
            printout += "%s- %s\n" % (i_count, str(item))
            i_count += 1

        return printout

if __name__ == "__main__":
    filepath = '../test/data/model152both'
    
    model = ReflectivityProblem(filepath)
    print(model)
    
    model.replace(range(24))
    print(model)

    
    
