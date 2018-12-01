import java.io.*;

public class Main {
  public static void main(String[] args) throws IOException {

        Runtime runtime = Runtime.getRuntime();
        String[] commands  = {"hostname"};
        Process process = runtime.exec(commands);

        BufferedReader lineReader = new BufferedReader(new InputStreamReader(process.getInputStream()));
        lineReader.lines().forEach(System.out::println);

        BufferedReader errorReader = new BufferedReader(new InputStreamReader(process.getErrorStream()));
        errorReader.lines().forEach(System.out::println);
    }
}
