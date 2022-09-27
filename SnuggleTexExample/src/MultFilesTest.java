//package uk.ac.ed.ph.snuggletex.samples;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import uk.ac.ed.ph.snuggletex.*;


import java.io.File;
import java.io.IOException;
import java.util.Scanner;

public class MultFilesTest {
        public void run(String[] fileNames) throws IOException {

            /* Create vanilla SnuggleEngine and new SnuggleSession */
            SnuggleEngine engine = new SnuggleEngine();
            SnuggleSession session = engine.createSession();

            for(String file : fileNames){
                runAFile(file, session);
            }
        }

        private void runAFile(String fileName, SnuggleSession session) throws IOException{
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

            XMLStringOutputOptions options = new XMLStringOutputOptions();
            options.setSerializationMethod(SerializationMethod.XHTML);
            options.setIndenting(true);
            options.setEncoding("UTF-8");
            options.setAddingMathSourceAnnotations(true);
            options.setUsingNamedEntities(true); /* (Only used if caller has an XSLT 2.0 processor) */


            String xmlStringEx = session.buildXMLString(options);
            System.out.println("Input " + inputEx.getString()
                    + " \n was converted to:\n" + xmlStringEx);
        }

    }

