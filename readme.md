# Introduction
This is a framework to generate texts from structured data.
It is part of my bachelor's thesis and allows you to preprocess your data into a readable format for ML models.
You can either define your own data preprocessing programs or use the ones that come with this package.
The model that is included is the [DataText Transformer Model by gongliym](https://github.com/gongliym/data2text-transformer/).
The included data_extract.py is based on the data_extract provided with the gongliym Transformer, but instead of preprocessing NBA Data it allows you to use NFL Data with the same format.
Furthermore the UDE.py is the Universal Data Extraction, which should allow you to preprocess any kind of data as long as it follows the format provided by newformat.json,
which should make creating readable datasets more general, easier and more accessible. (For format see data/Testing Data/newformat.json)

# Usage
Define the parameters for the model you're going to use in model_params.cfg. The parametes and values for them have to be separated by a comma; separation with newlines is
just for the readability and can be omitted.
To use the framework, simply start Data2Text.py. By default it will start the data extraction for the small_NFL dataset, then extract the vocabulary, split the data into training and validation sets, binarize the data to be a viable input for the model and then start the model with this data.

# Parameters
```
-data [file_location]                 #file location of your input data
-data_extractor [file_location]       #Ddata_extractor (default: UDE.py)
-vocab_extractor [file_location]      #vocab_extractor (default: extract_vocab.py)
-summary_preprocessor [file_location] #summary preprocessor (default: preprocess_summary_data.py)
-table_preprocessor [file_location]   #table data preprocessor (default: preprocess_table_data.py)
-table [table_data_output_name]       #output name of your table data
-summary [summary_data_output_name] 
-table_label [table_label_output_name]
-summary_label [summary_label_output_name]
-output_prefix [prefix]
-model [model_path]
-model_parameters [parameter_file]
-split_data [bool]
-split_ratio [float]```
