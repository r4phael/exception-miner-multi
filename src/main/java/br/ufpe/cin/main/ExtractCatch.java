package br.ufpe.cin.main;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.OutputStream;
import java.io.FileOutputStream;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.StandardCopyOption;
import java.nio.file.Files;

import com.github.javaparser.JavaParser;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.Parameter;
import com.github.javaparser.ast.stmt.CatchClause;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;

public class ExtractCatch extends SimpleFileVisitor<Path> {

    // private static final String FILE_PATH =
    // "java-parser/src/main/resources/OTFSubSetFile.java-2-Extract
    // Method-37-writeTopDICT";

    public static void main(String[] args) throws Exception {

         if (args.length < 1) {
             throw new IllegalArgumentException("Not enough arguments!");
         }

        String FILE_PATH = args[0];
        //String FILE_PATH = "/home/r4ph21/desenv/exception-miner/src/main/resources/ArithmeticExceptionDemo.java";
        //String FILE_PATH = "/home/r4ph21/desenv/exception-miner/src/main/resources/Blabla.java";

        String OUTPUT_PATH = args[1];
        //String OUTPUT_PATH = "/home/r4ph21/desenv/exception-miner/output/example.java";

        CompilationUnit cu_before = StaticJavaParser.parse(new FileInputStream(FILE_PATH));

        cu_before.accept(new VoidVisitorAdapter<Void>() {

            /**
             * For every if-statement, see if it has a comparison using "!=". Change it to
             * "==" and switch the "then" and "else" statements around.
             * 
             * @return
             */
            @Override
            
            /*
                https://www.javadoc.io/doc/com.github.javaparser/javaparser-core/latest/com/github/javaparser/ast/stmt/CatchClause.html
            */
            public void visit(CatchClause cc, Void arg) {

                //String filePath = FILE_PATH; //.substring(FILE_PATH.lastIndexOf("-") + 1).replace(".java","");
                // System.out.println("Method Before Extracted from File: " + methodName);
                System.out.println("* getParameter: " + cc.getParameter());
                System.out.println(" * Position * " + cc.getBegin());
                System.out.println(" * Body * " + cc.getBody());
                System.out.println(" * Declaration * " + cc.getBody());


                try (FileOutputStream outFile = new FileOutputStream(OUTPUT_PATH)){
                    
                    Path outPath = Paths.get(OUTPUT_PATH);
                    Path originalPath = Paths.get(FILE_PATH);
                    Files.copy(originalPath, outPath, StandardCopyOption.REPLACE_EXISTING);
                    System.out.println("Done");

                } catch (IOException e) {
                    System.out.println("Error in saving the file in output folder:" + cc.getParameter().toString());
                    e.printStackTrace();
                }

 

            }
        }, null);

    }

}