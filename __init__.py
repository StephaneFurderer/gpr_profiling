# -*- coding: utf-8 -*-
"""Main module of pandas-profiling.

Docstring is compliant with NumPy/SciPy documentation standard:
https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt
See also for a short description of docstring:
https://stackoverflow.com/questions/3898572/what-is-the-standard-python-docstring-format
"""
import codecs
import gpr_profiling.templates as templates
from .describe import describe
from .report import to_html
import pandas as pd

NO_OUTPUTFILE = "gpr_profiling.no_outputfile"
DEFAULT_OUTPUTFILE = "gpr_profiling.default_outputfile"

class ProfileReport(object):
    """Generate a profile report from a Dataset stored as a pandas `DataFrame`.

    Used has is it will output its content as an HTML report in a Jupyter notebook.

    Attributes
    ----------
    df : DataFrame
        Data to be analyzed
    bins : int
        Number of bins in histogram.
        The default is 10.
    stats_df : pandas data frame
        Test results as run outside of the profiling library
        Contains three columns: Name, Description, Value(s)
        Supported variable types for value: bool, numeric, list, dict, dict_items
    excluded_metric_names : list
        Metric names to exclude from the gpr warning check. All metrics excluded from the
        warning check will be printed.

    Methods
    -------
    get_description
        Return the description (a raw statistical summary) of the dataset.
    get_rejected_variables
        Return the list of rejected variable or an empty list if there is no rejected variables.
    to_file
        Write the report to a file.
    to_html
        Return the report as an HTML string.
    """
    html = ''
    file = None

    def __init__(self, df, stats_df = pd.DataFrame(), excluded_metric_names=[], **kwargs):
        """Constructor see class documentation
        """
        sample = kwargs.get('sample', df.head())

        description_set = describe(df, **kwargs)

        self.html = to_html(sample, description_set, stats_df, excluded_metric_names)

        self.description_set = description_set

    def get_description(self):
        """Return the description (a raw statistical summary) of the dataset.

        Returns
        -------
        dict
            Containing the following keys:
                * table: general statistics on the dataset
                * variables: summary statistics for each variable
                * freq: frequency table
        """
        return self.description_set

    def get_rejected_variables(self, threshold=0.9):
        """Return a list of variable names being rejected for high
        correlation with one of remaining variables.

        Parameters:
        ----------
        threshold : float
            Correlation value which is above the threshold are rejected
        
        Returns
        -------
        list
            The list of rejected variables or an empty list if the correlation has not been computed.
        """
        variable_profile = self.description_set['variables']
        result = []
        if hasattr(variable_profile, 'correlation'):
            result = variable_profile.index[variable_profile.correlation > threshold].tolist()
        return  result

    def to_file(self, outputfile=DEFAULT_OUTPUTFILE):
        """Write the report to a file.
        
        By default a name is generated.

        Parameters:
        ----------
        outputfile : str
            The name or the path of the file to generale including the extension (.html).
        """
    
        if outputfile != NO_OUTPUTFILE:
            if outputfile == DEFAULT_OUTPUTFILE:
                outputfile = 'profile_' + str(hash(self)) + ".html"
            # TODO: should be done in the template
            with codecs.open(outputfile, 'w+b', encoding='utf8') as self.file:
                self.file.write(templates.template('wrapper').render(content=self.html))

    def to_html(self):
        """Generate and return complete template as lengthy string
            for using with frameworks.
        
        Returns
        -------
        str
            The HTML output.
        """
        return templates.template('wrapper').render(content=self.html)

    def _repr_html_(self):
        """Used to output the HTML representation to a Jupyter notebook
        
        Returns
        -------
        str
            The HTML internal representation.
        """
        return self.html

    def __str__(self):
        """Overwrite of the str method.
        
        Returns
        -------
        str
            A string representation of the object.
        """
        return "Output written to file " + str(self.file.name)
