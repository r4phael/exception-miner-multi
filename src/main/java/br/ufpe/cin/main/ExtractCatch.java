package br.ufpe.cin.main;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.SimpleFileVisitor;
import java.util.Arrays;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import java.nio.file.Files;

import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.stmt.CatchClause;
import com.github.javaparser.ast.visitor.ModifierVisitor;
import com.github.javaparser.ast.visitor.Visitable;
import com.github.javaparser.utils.SourceRoot;

public class ExtractCatch extends SimpleFileVisitor<Path> {

    private static final String SAMPLE_CSV_FILE = "./results.csv";

    public static void main(String[] args) throws Exception {

        if (args.length < 1) {
              throw new IllegalArgumentException("Not enough arguments!");
        }

        String PROJECT = args[0];
        String FILE_PATH = args[1];
        //String FILE_PATH = "/home/r4ph21/desenv/exception-miner/src/main/resources/";

        String FILE_NAME = args[2];
        String BEFORE_PATH = args[3];
        String AFTER_PATH = args[4];
        //String FILE_NAME = "ArithmeticExceptionDemo.java";
        //String fileName = FILE_PATH.substring(FILE_PATH.lastIndexOf("-") + 1).replace(".java","");

        SourceRoot sourceRoot = new SourceRoot(Paths.get(FILE_PATH));
        CompilationUnit cu = sourceRoot.parse("", FILE_NAME);

        cu.accept(new ModifierVisitor<Void>() {
            
            /*
                https://www.javadoc.io/doc/com.github.javaparser/javaparser-core/latest/com/github/javaparser/ast/stmt/CatchClause.html
            */
            public Visitable visit(CatchClause cc, Void arg) {

                //String filePath = FILE_PATH; //.substring(FILE_PATH.lastIndexOf("-") + 1).replace(".java","");
                //System.out.println(cc.getMetaModel());
                //System.out.println("* getParameter: " + cc.getParameter());
                //System.out.println(" * Position * " + cc.getBegin());
                //System.out.println(" * Body * " + cc.getBody());
                //System.out.println(cc.getBody());
                //System.out.println(" * Begin Line * " + cc.getBegin());
                //System.out.println(" * End Line * " + cc.getEnd());

                try {
                                        
                    //Saving the File before transformations
                    sourceRoot.saveAll(Paths.get(BEFORE_PATH));

                    //Saving the metadata from .java files
                    try (
                        BufferedWriter writer = Files.newBufferedWriter(Paths.get(SAMPLE_CSV_FILE));
            
                        CSVPrinter csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT
                                .withHeader("Project", "FileName", "FilePath", "CatchClauseMetaModel", "Parameters", "Body", "Begin", "End"));
                    ) {       
                        cc.getBegin();
                        csvPrinter.printRecord(Arrays.asList(PROJECT,
                            FILE_NAME,
                            FILE_PATH,
                            cc.getMetaModel(), 
                            cc.getParameter(), 
                            cc.getBody(),
                            cc.getBegin().map(Object::toString).orElse(null).toString(),
                            cc.getEnd().map(Object::toString).orElse(null).toString()));
                        csvPrinter.flush();
                
                    } catch (IOException e) {
                        System.out.println("Error saving the results.csv in the output folder:" + cc.getParameter().toString());
                        e.printStackTrace();
                    }
                    
                    //Transforming the catch clause
                    cc.getParameter().setType(Exception.class);                 
    
                    //Saving the .java file after transformations
                    //System.out.println(cu.toString());
                    sourceRoot.saveAll(Paths.get(AFTER_PATH));
                    //System.out.println("Done");

                } catch (Exception e) {
                    System.out.println("error saving and parsing .java files in the output folder:" + cc.getParameter().toString());
                    e.printStackTrace();
                }

                return super.visit(cc, arg);

            }
        }, null);

    }

}