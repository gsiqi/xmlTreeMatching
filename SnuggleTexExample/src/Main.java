import java.io.IOException;
import java.nio.channels.MulticastChannel;

public class Main {

    public static void main(String[] args) {
        String[] fileNames = args;

        //test the software connects and converts at all
        Test1 test = new Test1();
        try{
            test.run(fileNames[0]);
        }catch(IOException ex){
            ex.printStackTrace();
        }

        System.out.println();
        System.out.println();

        //test multi files to see if it works for many examples
        MultFilesTest test2 = new MultFilesTest();
        try{
            test2.run(fileNames);
        }catch (IOException ex){
            ex.printStackTrace();
        }
    }
}
