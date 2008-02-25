<?php
/**
 *	List functions for lists of values.
 *	@package mirror 
 *	@subpackage lib
 *	@author Mike Morgan <mike.morgan@oregonstate.edu> 
 *	
 *	Usage example:
 *	<code>
 *	$orderby=get_order();
 *	$query="SELECT * FROM fic_courses $orderby";
 *	$courses=db_get($query,MYSQL_ASSOC);
 *	$headers=array(
 *		'course_id'=>'',
 *		'title'=>'Course Title',
 *		'date_start_course'=>'Start',
 *		'date_end_course'=>'End',
 *		'date_start_reg'=>'Reg Starts',
 *		'date_end_reg'=>'Reg Ends',
 *		'active'=>'Active?',
 *		'entry_date'=>'Created'
 *	);
 *	show_list($courses,$headers);
 *	</code>
 *
 *	Accompanying CSS for table output:
 *	<code>
 *	.list
 *	{
 *		border:1px solid #999;
 *	}
 *	.list th
 *	{
 *		background:#eee;
 *		border:1px solid #000;
 *		font-weight:bold;
 *	}
 *	.list th a
 *	{
 *		display:block;
 *		padding:0 14px;
 *	}
 *	.list th a:hover
 *	{
 *		background-color:#fff;
 *	}
 *	.row1
 *	{
 *		background:#ddd;
 *	}
 *	.row2
 *	{
 *		background:#ccc;
 *	}
 *	.row1:hover, .row2:hover
 *	{
 *		background-color:#fec;
 *	}
 *	.current-sort
 *	{
 *		background:#fda;
 *	}
 *	.sort-desc
 *	{
 *		background:#fec url(../img/up.gif) no-repeat right;
 *	}
 *	.sort-asc
 *	{
 *		background:#fec url(../img/down.gif) no-repeat right;
 *	}
 *	</code>

 *	Accompanying JavaScript for select all / inverse:
 *	<code>
 *	<script type="text/javascript">
 *	//<!--
 *	function selectAll(formObj,invert)
 *	{
 *		for (var i=0;i < formObj.elements.length;i++)
 *		{
 *			fldObj = formObj.elements[i];
 *			if (fldObj.type == 'checkbox')
 *			{
 *				if (invert==1)
 *				{
 *					fldObj.checked = (fldObj.checked) ? false : true;
 *				}
 *				else
 *				{
 *					fldObj.checked = true;
 *				}
 *			}
 *		}
 *	}
 *	//-->
 *	</script>
 *	</code>
 */

/**
 *	Show a list of values, for forms.
 *	@param array $list associative array
 *	@param array $headers column name => column title (for table heads)
 *	@param string $type checkbox, radio, simple
 *	@param array $array actions to display in actions select list 
 *	@param string $form_id id of form holding list
 *	@param bool $sortable whether or not to show sortable column headers (links in th's)
 *	@param array|string $selected if type is checkbox, array otherwise string with one val
 */
function show_list($list,$headers,$type='checkbox',$actions=null,$form_id=null,$sortable=true,$selected=null)
{
	if ( is_array($list) && count($list)>0 && is_array($headers) )
	{
		if ( $type!='simple' && !empty($_GET['sort']) && !empty($_GET['order']) )
		{
			form_hidden('sort',$_GET['sort']);
			form_hidden('order',$_GET['order']);
		}
		echo "\n".'<table class="list">';
		show_headers($headers,$type,$sortable);
		echo "\n".'<tbody>';

        $count = 0;
		foreach ($list as $row)
		{
			show_row($headers,$row,$type,$count++,$selected);
		}
		echo "\n".'</tbody>';
		echo "\n".'</table>';
		if ($type=='checkbox')
		{
echo <<<js
<script type="text/javascript">
//<!--
function list_select(formObj,invert)
{
	for (var i=0;i < formObj.elements.length;i++)
	{
		fldObj = formObj.elements[i];
		if (fldObj.type == 'checkbox')
		{
			if (invert==1)
			{
				fldObj.checked = (fldObj.checked) ? false : true;
			}
			else
			{
				fldObj.checked = true;
			}
		}
	}
}
//-->
</script>
js;
			echo "\n".'<p><input type="button" name="selectall" onclick="list_select(this.form,0);" class="button2" value="Select All"/> <input type="button" name="selectall" onclick="list_select(this.form,1);" class="button2" value="Invert"/></p>';
		}
		if ($type=='radio'||$type='checkbox-small')
		{
			echo '<br />';	
		}
		if (is_array($actions)&&$type!='simple')
		{
			if (count($actions) == 1) {
				$actions = array_values($actions);
				echo '<p>';
				form_submit('submit','submit','button1',$actions[0].' &raquo;');
				echo '</p>';
			} else {
				echo '<p>';
				echo '<label for="action">With selected: </label>';
				form_select('action','action','text2',$actions,'');
				form_submit('submit','submit','button1','Go &raquo;');
				echo '</p>';
			}
		}
	}
	elseif ( !is_array($headers) )
	{
		echo "\n".'<h1>FIX HEADERS ARRAY</h1>';
	}
	else
	{
		echo "\n".'<p>No records found.</p>';
	}
}

/**
 *	Show table headers.
 *	@param array $headers column name => column title (for table heads)
 *	@param string $type type of list that is being shown
 *	@param bool $sortable whether or not to show sortable column headers (links in th's)
 */
function show_headers($headers,$type,$sortable=true)
{
	echo "\n".'<thead><tr>';
	$sort=$_GET['sort'];
	$order=get_order();
	$count=0;
	foreach ($headers as $col=>$title)
	{
		if ( !empty($sort) && !empty($order) )
		{
			if ($col==$sort && $order=='ASC')
			{
				$a_class=' class="sort-asc current-sort" ';
			}
			elseif ($col==$sort && $order=='DESC')
			{
				$a_class=' class="sort-desc current-sort" ';
			}
			else
			{
				$a_class=null;
			}
		}
		if ($type!='simple'&&$count==0)	
		{
			echo "\n".'<th> </th>';
		}
		elseif($sortable)
		{
			$qs = array();
			foreach ($_GET as $qn=>$qv) { $qs[$qn] = $qv; } // existing query string variables
			$qs['sort'] = $col; // add/replace sort to query string
			$qs['order'] = $order; // add/replace order by to query string
			foreach ($qs as $qn=>$qv) { $querystring[] = $qn.'='.$qv; } // existing query string variables
			echo "\n".'<th><a '.$a_class.'href="'.$_SERVER['PHP_SELF'].'?'.implode('&amp;',$querystring).'">'.$title.'</a></th>';
			unset($qs);
			unset($querystring);
		}
		else
		{
			echo "\n".'<th>'.$title.'</th>';
		}
		$count++;
	}
	echo "\n".'</tr></thead>';
}

/**
 *	Show table data.
 *	@param array $headers column name => column title (for knowing which ones to display)
 *	@param array $row table row, assoc
 *	@param string $type type of table, determines first column, which could be an input
 *	@param array|string $selected selected items; if type is checkbox, array otherwise string with one val
 */
function show_row($headers,$row,$type,$num=null,$selected=null)
{
	$indexes=array_keys($headers);
	$idname = $indexes[0];
	$count=0;
	$tr_class=($num%2)?' class="row1" ':' class="row2" ';
	echo "\n".'<tr'.$tr_class.'>';
	foreach ($indexes as $index)
	{
		$row[$index]=clean_out($row[$index]);
		if ($type!='simple'&&$count==0)
		{
			$id=preg_replace('/[^[:alnum:]]/', '', $index).$row[$index];
			if ($type=='checkbox'||$type=='checkbox-small')
			{
				echo "\n".'<td>';
				form_checkbox($idname.'[]',$id,null,$row[$index],(is_array($selected) && in_array($row[$index], $selected)));
				echo "\n".'</td>';
			}
			elseif ($type=='radio')
			{
				echo "\n".'<td>';
				form_radio($idname,$id,null,$row[$index], ($row[$index] == $selected));
				echo "\n".'</td>';
			}
		}
		else
		{
			echo ($type=='simple')?"\n".'<td>'.$row[$index].'</td>':"\n".'<td><label for="'.$id.'">'.$row[$index].'</label></td>';
		}
		$count++;
	}
	echo "\n".'</tr>';
}

/**
 *	Determine current sort order.
 */
function get_order()
{
	return ($_GET['order']=='ASC')?'DESC':'ASC';
}

/**
 *	Determine whether or not list is currently sorted.
 *	@param string $method which http method to check for sort information
 *	@return mixed cleaned orderby clause based on saved sort information or null if no orderby is set in the defined method
 */
function get_orderby($method='get')
{
	if ( $method=='get' && !empty($_GET['sort']) && !empty($_GET['order']) )
	{
		$sort=clean_in($_GET['sort']);
		$order=clean_in($_GET['order']);
		return " ORDER BY $sort $order ";
	}
	elseif ( $method=='post' && !empty($_POST['sort']) && !empty($_POST['order']) )
	{
		$sort=clean_in($_POST['sort']);
		$order=clean_in($_POST['order']);
		return " ORDER BY $sort $order ";
	}
	elseif ( $method=='session' && !empty($_SESSION['sort']) && !empty($_SESSION['order']) )
	{
		$sort=clean_in($_SESSION['sort']);
		$order=clean_in($_SESSION['order']);
		return " ORDER BY $sort $order ";
	}
	else return null;
}

/**
 *	Parses $_POST for ids, shows edit forms for each id with populated data.
 *	<ul>
 *	<li>name will be used to retrieve an _array_ from $_POST of the same name</li>
 *		<li>the form will be an include, with $posts[col_name] as the default for all values</li>
 *		<li>try to keep your query simple (no crazy sorting, etc.) -- we're talking one record at a time here anyway</li>
 *	</ul>
 *	Example:
 *	<code>
 *	list_edit_ids('course_id','../forms/course.php','SELECT * FROM fic_courses','1');
 *	</code>
 *	@param string $name name of id field
 *	@param string $form path to form to be used to items
 *	@param string $q_front front half of query
 *	@param string $q_where where statement
 *	@param array $dates array of date field names, so they can be fixed for forms
 *	@param array $datetimes array of datetime field names, so they can be fixed for forms
 */
function list_edit_ids($name,$form,$q_front,$q_where='1',$dates=null,$datetimes=null)
{
	if ( !empty($_SESSION[$name]) && is_array($_SESSION[$name]) )
	{
		$ids=implode(',',$_SESSION[$name]);
		$orderby=get_orderby('session');
		$query=$q_front.' WHERE '.$q_where." AND $name IN($ids) ".$orderby;
		$records=db_get($query);
		form_start($name);
		foreach ($records as $record)
		{
			echo "\n".'<div class="record">';
			$record=form_array_fix_dates($dates,$datetimes,2,$record);
			foreach ($record as $key=>$val)
			{
				$posts[$key]=clean_out($val);
			}
			include($form);
			echo "\n".'<div class="record-submit">';
			form_submit('submit', '', 'button1');
			echo "\n".'</div>';
			echo "\n".'</div>';
		}
		form_end();
	}
	else
	{
		echo '<p>You must select a record.  <a href="javascript:history.back();">Go back</a>.</p>';
	}
}

/**
 *	Process a submitted list_edit_ids form.
 *	@param array $name array of primary ids posted from the form, these are vital to the WHERE clause of the UPDATE statements.
 *	@param string $table name of table being affected
 */
function list_update_ids($name,$table)
{
	$keys=array_keys($_POST[$name]);
	foreach ($keys as $index)
	{
		foreach ($_POST as $key=>$val)
		{
			if ($key!='submit')
			{
				$posts[$index][$key]=$val[$index];
			}
		}
	}
	foreach ($posts as $dataset)
	{
		$query=db_makeupdate($dataset,$table," WHERE $name='".$dataset[$name]."' ");
		db_query($query);
	}
}
?>
