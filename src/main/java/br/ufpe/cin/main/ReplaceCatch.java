package br.ufpe.cin.main;

import java.io.BufferedWriter;
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
import java.util.Arrays;
import java.util.Optional;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;

import java.nio.file.Files;

import com.github.javaparser.JavaParser;
import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.body.Parameter;
import com.github.javaparser.ast.stmt.CatchClause;
import com.github.javaparser.ast.visitor.ModifierVisitor;
import com.github.javaparser.ast.visitor.Visitable;
import com.github.javaparser.ast.visitor.VoidVisitorAdapter;
import com.github.javaparser.utils.SourceRoot;

import com.github.javaparser.ast.type.Type;

public class ReplaceCatch extends SimpleFileVisitor<Path> {

    // private static final String FILE_PATH =
    // "java-parser/src/main/resources/OTFSubSetFile.java-2-Extract
    // Method-37-writeTopDICT";

    private static final String SAMPLE_CSV_FILE = "./results.csv";
    //protected static final Parameter Exception = ;
    protected static final Parameter Exception = null;

    public static void main(String[] args) throws Exception {

        // if (args.length < 1) {
        //       throw new IllegalArgumentException("Not enough arguments!");
        // }

        //String FILE_PATH = args[0];
        String FILE_PATH = "/home/r4ph21/desenv/exception-miner/src/main/resources/";
        //String FILE_PATH = "/home/r4ph21/desenv/exception-miner/output/elasticsearch-hadoop/LicenseHeadersTask.java";

        //String OUTPUT_PATH = args[1];
        //FileInputStream OutputFile = new FileInputStream(FILE_PATH);
        //CompilationUnit cu = StaticJavaParser.parse(new FileInputStream(FILE_PATH));

        SourceRoot sourceRoot = new SourceRoot(Paths.get(FILE_PATH));
        CompilationUnit cu = sourceRoot.parse("", "example.java");
        

        cu.accept(new ModifierVisitor<Void>() {

            public Visitable visit(CatchClause cc, Void arg) {

                //System.out.println("############");
                //System.out.println(cc.getParameter());
                
                // Parameter p = new Parameter();
                // CatchClause genException = new CatchClause();
                // p.setName("ex");
                // p.setType(Exception.class);
                // genException.setParameter(p);
                //cc.replace(genException);

                try{

                    //cc.getParameter().setName("ex");
                    cc.getParameter().setType(Exception.class);                 
    
                    System.out.println(cu.toString());
                    sourceRoot.saveAll(Paths.get("output/dataset/after/"));
         

                } catch (Exception e) {
                        System.out.println("error in replacing the catch clause with a generic or saving new .java from file:" + cc.getParameter().toString());
                        e.printStackTrace();
                }
                
                return super.visit(cc, arg);
            

            }
        }, null);


    }

}