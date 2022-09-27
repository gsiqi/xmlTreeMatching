//package uk.ac.ed.ph.snuggletex.samples;
import org.w3c.dom.NodeList;
import uk.ac.ed.ph.snuggletex.SnuggleInput;
import uk.ac.ed.ph.snuggletex.SnuggleEngine;
import uk.ac.ed.ph.snuggletex.SnuggleSession;


import java.io.File;
import java.io.IOException;
import java.util.Scanner;


public class Test1 {
    public Test1 (){}
    public void run(String fileName) throws IOException{

        /* Create vanilla SnuggleEngine and new SnuggleSession */
        SnuggleEngine engine = new SnuggleEngine();
        SnuggleSession session = engine.createSession();

        /* Parse some very basic Math Mode input */
        SnuggleInput input = new SnuggleInput("$$ x+2=3 $$");
        session.parseInput(input);

        /* Convert the results to an XML String, which in this case will
         * be a single MathML <math>...</math> element. */
        String xmlString = session.buildXMLString();
        System.out.println("Input " + input.getString()
                + " was converted to:\n" + xmlString);



        /*try parsing the info that I am feeding it */
        File file = new File(fileName);
        Scanner scanner = new Scanner(file);
        String data = "";
        while(scanner.hasNext()){
            data += scanner.nextLine();
        }
        SnuggleInput inputEx = new SnuggleInput(data);
        session.reset();
        session.parseInput(inputEx);

        /* Convert the results to an XML String, which in this case will
         * be a single MathML <math>...</math> element. */
        String xmlStringEx = session.buildXMLString();
        System.out.println("Input " + inputEx.getString()
                + " was converted to:\n" + xmlStringEx);

            //// not entirely sure what this does? what a DOM subtree is?
//        NodeList nodeList = session.buildDOMSubtree();   //i could start this from a specific node, so only part of the tree but im not sure where I'd want that to start?
//        for(int i = 0; i < nodeList.getLength(); ++i){
//            System.out.println(nodeList.item(i));
//        }

    }

}
