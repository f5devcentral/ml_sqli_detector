Lab 1
=======

`Last updated: 2022-04-11 3:00 PM EST`

Jupyter notebooks
-----------------

Jupyter notebook is a web-based application suitable for capturing the whole computation process: developing, documenting, and executing code, as well as communicating the results. The Jupyter notebook combines two components:

 - A web application: a browser-based tool for interactive authoring of documents which combine explanatory text, mathematics, computations and their rich media output.

 - Notebook documents: a representation of all content visible in the web application, including inputs and outputs of the computations, explanatory text, mathematics, images, and rich media representations of objects.


Strusture of notebook documents
-------------------------------

The notebook consists of a sequence of cells. A cell is a multiline text input field, and its contents can be executed by using Shift-Enter, or by clicking either the “Play” button the toolbar, or Cell, Run in the menu bar. The execution behavior of a cell is determined by the cell's type. There are three types of cells: code cells, markdown cells, and raw cells

Code cells
~~~~~~~~~~

Code cells contain the code itself, with full syntax highlighting and tab completion. programming language depends on the kernel and the default kernel (IPython) runs Python code.

Markdown cells
~~~~~~~~~~~~~~

The Markdown language provides a simple way to perform text markup. Document structure can be created using Markdown headings (1 to 6 hash # signs)

Raw cells
~~~~~~~~~

Raw cells provide a place in which you can write output directly. Raw cells are not evaluated by the notebook. 

Open existing Jupyter Notebook
------------------------------

1. In the running deployment click :guilabel:`ACCESS` -> :guilabel:`JUPYTER` then enter password `jupyter` and click  :guilabel:`Log in`

    .. image:: static/access.png

2. Navigate to `ml_sql_detector` directory and click on `ml_sqli_detector-distilbert.ipynb`

    .. image:: static/ipynb.png


Import packages and load data set
---------------------------------

1. Highlight first code cell and click :guilabel:`Run`

    .. image:: static/run.png

.. note:: Code cell status (shown in `[ ]:` brackets), will change to :guilabel:`*` while kernel is running the code. And change to :guilabel:`<step number>` when execution is complete. I.e. for completed step 1 it will show :guilabel:`[1]:`


2. Wait until the execution is complete and run code cells #2 #3 and #4

Our training data set is now successfully loaded

Train the Distilbert model
--------------------------

1. Run the code cells #5 and #7 to load the pre-trained model and freeze most of the layers. Freezing will render the weights "untrainable" in the corresponding "frozen" layers allowing for an effective transfer learning while keeping the outermost layers receptible to training

2. `ktrain` has a function that looks for the optimal learning rate of a given model ( i.e. how far to turn the knob), and can be very helpful especially for relatively simple models:

    .. code-block:: python

        learner.lr_find(show_plot=True, max_epochs=2)

.. note:: We will skip this step in order to save time - `lr.find()` function can take a long time to complete...

3. The following function will perform the model training using a single cycle of 2 epochs and pre-determined optimal learning rate of `3e-5`. Run the code cell to begin training:

    .. code-block:: python

        learner.fit_onecycle(3e-5, 2)
    
4. Save the predictor by running the following code cell:

    .. code-block:: python

        predictor = ktrain.get_predictor(learner.model, preproc)
        predictor.save('/home/jupyter/detector_model_lab')
        print('MODEL SAVED')

5. Run a one or two predictions using our trained model - run code cells that load the model and provide the inference on the input text:

    .. code-block:: python

        predictor = ktrain.load_predictor('/home/jupyter/detector_model_lab')
        new_model = ktrain.get_predictor(predictor.model, predictor.preproc)

    .. code-block:: python

        text = '<applet onkeydown="alert(1)" contenteditable>test</applet>'
        result = new_model.predict(text)
        print(result)

|


Next: |lab2|

.. |lab2| raw:: html

            <a href="https://github.com/sstarzh/ml_sqli_detector/blob/main/lab2.rst" target="_blank">Lab 2: Serve the model</a>

.. |jupyter| raw:: html

            <a href="https://jupyter-notebook.readthedocs.io/en/latest" target="_blank">The Jupyter Notebook</a>