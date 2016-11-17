package edu.umass.cs.mallet.grmm.learning;

import bsh.EvalError;
import edu.umass.cs.mallet.base.pipe.*;
import edu.umass.cs.mallet.base.pipe.iterator.LineGroupIterator;
import edu.umass.cs.mallet.base.pipe.iterator.PipeInputIterator;

import edu.umass.cs.mallet.base.types.InstanceList;

import edu.umass.cs.mallet.base.util.*;


import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;

import java.io.IOException;

import java.util.ArrayList;
import java.util.Arrays;

import java.util.LinkedList;
import java.util.List;
import java.util.logging.Logger;
import java.util.regex.Pattern;

public class AcrfForTestJoty {

	
	private static CommandOption.File modelFile = new CommandOption.File(
			AcrfForTestJoty.class, "model-file", "FILENAME", true, null,
			"gz file describing learned model.", null);

	private static CommandOption.File testFile = new CommandOption.File(
			AcrfForTestJoty.class, "testing", "FILENAME", true, null,
			"File containing testing data.", null);
	
	 private static CommandOption.String evalOption = new CommandOption.String
     (GenericAcrfTui.class, "eval", "STRING", true, "LOG",
             "Evaluator to use.  Java code grokking performed.", null);


	private static BshInterpreter interpreter = setupInterpreter();

	public static void main(String[] args) throws IOException, EvalError {
		
		doProcessOptions(AcrfForTestJoty.class, args);
		ACRF acrf = (ACRF) FileUtils.readObject(modelFile.value);
		//System.out.println("model file loaded!");
		Pipe pipe = acrf.getInputPipe();
	
		PipeInputIterator testSource;
		if (testFile.wasInvoked()) {
			testSource = new LineGroupIterator(new FileReader(testFile.value),
					Pattern.compile("^\\s*$"), true);
		} else {
			testSource = null;
		}

		InstanceList testing = new InstanceList(pipe);
		testing.add(testSource);

		//System.out.println("testing is ready to start getting marginals!");
		// acrf.getMarginalsJoty (testing);
      
		ACRFEvaluator eval = createEvaluator (evalOption.value);
	
		eval.test (acrf, testing, "Testing");

	}

	
	private static BshInterpreter setupInterpreter() {
		BshInterpreter interpreter = CommandOption.getInterpreter();
		try {
			interpreter.eval("import edu.umass.cs.mallet.base.extract.*");
			interpreter.eval("import edu.umass.cs.mallet.grmm.inference.*");
			interpreter.eval("import edu.umass.cs.mallet.grmm.learning.*");
			interpreter
					.eval("import edu.umass.cs.mallet.grmm.learning.templates.*");
		} catch (EvalError e) {
			throw new RuntimeException(e);
		}

		return interpreter;
	}

	public static void doProcessOptions(Class childClass, String[] args) {
		CommandOption.List options = new CommandOption.List("",
				new CommandOption[0]);
		options.add(childClass);
		options.process(args);
		options.logOptions(Logger.getLogger(""));
	}

	private static ACRF.Template[] parseModelFile(File mdlFile)
			throws IOException, EvalError {
		BufferedReader in = new BufferedReader(new FileReader(mdlFile));

		List tmpls = new ArrayList();
		String line = in.readLine();
		while (line != null) {
			Object tmpl = interpreter.eval(line);
			if (!(tmpl instanceof ACRF.Template)) {
				throw new RuntimeException("Error in " + mdlFile + " line "
						+ in.toString() + ":\n  Object " + tmpl
						+ " not a template");
			}
			tmpls.add(tmpl);
			line = in.readLine();
		}

		return (ACRF.Template[]) tmpls.toArray(new ACRF.Template[0]);
	}

	 public static ACRFEvaluator createEvaluator (String spec) throws EvalError
	  {
	    if (spec.indexOf ('(') >= 0) {
	      // assume it's Java code, and don't screw with it.
	      return (ACRFEvaluator) interpreter.eval (spec);
	    } else {
	      LinkedList toks = new LinkedList (Arrays.asList (spec.split ("\\s+")));
	      return createEvaluator (toks);
	    }
	  }

	  private static ACRFEvaluator createEvaluator (LinkedList toks)
	  {
	    String type = (String) toks.removeFirst ();

	    if (type.equalsIgnoreCase ("SEGMENT")) {
	      int slice = Integer.parseInt ((String) toks.removeFirst ());
	      if (toks.size() % 2 != 0)
	        throw new RuntimeException ("Error in --eval "+evalOption.value+": Every start tag must have a continue.");
	      int numTags = toks.size () / 2;
	      String[] startTags = new String [numTags];
	      String[] continueTags = new String [numTags];

	      for (int i = 0; i < numTags; i++) {
	        startTags[i] = (String) toks.removeFirst ();
	        continueTags[i] = (String) toks.removeFirst ();
	      }

	      return new MultiSegmentationEvaluatorACRF (startTags, continueTags, slice);

	    } else if (type.equalsIgnoreCase ("LOG")) {
	      return new ACRFTrainer.LogEvaluator ();

	    } else if (type.equalsIgnoreCase ("SERIAL")) {
	      List evals = new ArrayList ();
	      while (!toks.isEmpty ()) {
	        evals.add (createEvaluator (toks));
	      }
	      return new AcrfSerialEvaluator (evals);

	    } else {
	      throw new RuntimeException ("Error in --eval "+evalOption.value+": illegal evaluator "+type);
	    }
	  }
}

